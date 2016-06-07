import os
import json
import time
import logging

import celery
from django.conf import settings
from django.core.cache import caches
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from django.utils.crypto import get_random_string
from django.views.generic.base import View
import requests

from regulations import tasks
from regulations import docket
from regulations.views.preamble import (
    common_context, CommentState, generate_html_tree, first_preamble_section,
    notice_data)

logger = logging.getLogger(__name__)

# TODO: Expire preview URL at commenting deadline
PREVIEW_EXPIRATION_SECONDS = 60 * 60 * 24 * 90


def upload_proxy(request):
    """Create a random key name and a pair of temporary PUT and GET URLS to
    permit attachment uploads and previews from the browser.
    """
    filename = request.GET['name']
    size = int(request.GET['size'])
    valid, message = validate_attachment(filename, size)
    if not valid:
        logger.error(message)
        return JsonResponse({'message': message}, status=400)
    key, put_url = tasks.SignedUrl.generate(
        method='put_object',
        params={
            'ContentLength': size,
            'ContentType': request.GET.get('type', 'application/octet-stream'),
            'Metadata': {'name': filename},
        },
    )
    disposition = 'attachment; filename="{}"'.format(filename)
    _, get_url = tasks.SignedUrl.generate(
        key=key,
        params={
            'ResponseExpires': time.time() + PREVIEW_EXPIRATION_SECONDS,
            'ResponseContentDisposition': disposition,
        },
    )
    return JsonResponse({
        'urls': {'get': get_url, 'put': put_url},
        'key': key,
    })


@csrf_exempt
@require_http_methods(['POST'])
def preview_comment(request):
    """Convert a comment to PDF, upload the result to S3, and return a signed
    URL to GET the PDF.
    """
    body = json.loads(request.body.decode('utf-8'))
    sections = body.get('assembled_comment', [])
    html = tasks.json_to_html(sections, mark_as_draft=True)
    key = '/'.join([settings.ATTACHMENT_PREVIEW_PREFIX, get_random_string(50)])
    document_number = tasks.get_document_number(sections)
    content_disposition = tasks.generate_content_disposition(
        document_number, draft=True)
    with tasks.html_to_pdf(html) as pdf:
        tasks.s3_client.put_object(
            Body=pdf,
            ContentType='application/pdf',
            ContentDisposition=content_disposition,
            Bucket=settings.ATTACHMENT_BUCKET,
            Key=key,
        )
    _, url = tasks.SignedUrl.generate(key=key)
    return JsonResponse({'url': url})


regs_gov_fmt = 'https://www.regulations.gov/#!documentDetail;D={document}'


class SubmitCommentView(View):

    def get(self, request, doc_number):
        preamble, _, _ = notice_data(doc_number)
        section = first_preamble_section(preamble)
        if section is None:
            raise Http404
        return redirect(
            'chrome_preamble', paragraphs='/'.join(section['label']))

    def post(self, request, doc_number):
        form_data = {
            key: value for key, value in request.POST.items()
            if key != 'comments'
        }
        comments = json.loads(request.POST.get('comments', '[]'))

        context = common_context(doc_number)

        if context['meta']['comment_state'] != CommentState.OPEN:
            raise Http404("Cannot comment on {}".format(doc_number))

        context.update(generate_html_tree(context['preamble'], request,
                                          id_prefix=[doc_number, 'preamble']))
        context['comment_mode'] = 'write'
        context.update({'message': '', 'metadata_url': ''})

        valid, context['message'] = self.validate(comments, form_data)
        context['regs_gov_url'] = regs_gov_fmt.format(
            document=settings.COMMENT_DOCUMENT_ID)

        # Catch any errors related to enqueueing comment submission. Because
        # this step can fail for many reasons (e.g. no connection to broker,
        # broker fails to write, etc.), catch `Exception`.
        try:
            _, context['metadata_url'] = self.enqueue(comments, form_data)
        except Exception as exc:
            logger.exception(exc)

        template = 'regulations/comment-confirm-chrome.html'
        return TemplateResponse(request=request, template=template,
                                context=context)

    def validate(self, comments, form_data):
        valid, message = docket.sanitize_fields(form_data)
        if not valid:
            logger.error(message)
            return valid, message

        files = tasks.extract_files(comments)
        # Account for the main comment itself submitted as an attachment
        if len(files) > settings.MAX_ATTACHMENT_COUNT - 1:
            message = "Too many attachments"
            logger.error(message)
            return False, message

        return True, ''

    def enqueue(self, comments, form_data):
        metadata_url = tasks.SignedUrl.generate()
        chain = celery.chain(
            tasks.submit_comment.s(comments, form_data, metadata_url),
            tasks.publish_tracking_number.s(metadata_url=metadata_url),
        )
        chain.delay()
        return metadata_url


@require_http_methods(['GET', 'HEAD'])
def get_federal_agencies(request):
    return lookup_regulations_gov(field='gov_agency',
                                  dependentOnValue='Federal')


@require_http_methods(['GET', 'HEAD'])
def get_gov_agency_types(request):
    return lookup_regulations_gov(field='gov_agency_type')


def lookup_regulations_gov(*args, **kwargs):
    """ GET lookup values from regulations.gov. Use a cache """
    cache = caches['regs_gov_cache']
    cache_key = make_cache_key(**kwargs)
    response = cache.get(cache_key)

    if response is None:
        logger.debug("Looking up in regs.gov")
        response = requests.get(
            settings.REGS_GOV_API_LOOKUP_URL,
            params=kwargs,
            headers={'X-Api-Key': settings.REGS_GOV_API_KEY}
        )
        if response.status_code == requests.codes.ok:
            response = JsonResponse(response.json()['list'], safe=False)
            cache.set(cache_key, response)
        else:
            logger.error("Failed to lookup regulations.gov: {}",
                         response.status_code, response.text)
            response.raise_for_status()
    return response


def validate_attachment(filename, size):
    if size <= 0 or size > settings.ATTACHMENT_MAX_SIZE:
        return False, "Invalid attachment size"
    _, ext = os.path.splitext(filename)
    if ext[1:].lower() not in settings.VALID_ATTACHMENT_EXTENSIONS:
        return False, "Invalid attachment type"
    return True, ""


def make_cache_key(*args, **kwargs):
    """ Make a cache key of the form key1:value1:key2:value2.
        Sort the keys to ensure repeatability
    """
    return ":".join((key + ":" + str(kwargs[key]) for key in sorted(kwargs)))

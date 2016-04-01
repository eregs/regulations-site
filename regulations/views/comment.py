import os.path
import json
import logging

import celery
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from regulations import tasks
import requests

logger = logging.getLogger(__name__)


def upload_proxy(request):
    """Create a random key name and a temporary upload URL to permit uploads
    from the browser.
    """
    filename = request.GET['name']
    size = int(request.GET['size'])
    valid, message = validate_attachment(filename, size)
    if not valid:
        logger.error(message)
        return JsonResponse({'message': message}, status=400)
    s3 = tasks.make_s3_client()
    key = get_random_string(50)
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'ContentLength': size,
            'ContentType': request.GET.get('type', 'application/octet-stream'),
            'Bucket': settings.ATTACHMENT_BUCKET,
            'Key': key,
            'Metadata': {'name': filename}
        },

    )
    return JsonResponse({
        'url': url,
        'key': key,
    })


@csrf_exempt
@require_http_methods(['POST'])
def preview_comment(request):
    body = json.loads(request.body.decode('utf-8'))
    content = tasks.build_comment(body)
    return HttpResponse(content, 'text/markdown', 200)


@csrf_exempt
@require_http_methods(['POST'])
def submit_comment(request):
    """Submit a comment to the task queue."""
    body = json.loads(request.body.decode('utf-8'))

    comment = tasks.build_comment(body)
    if len(comment) > settings.MAX_COMMENT_LENGTH:
        message = "Comment is too long"
        logger.error(message)
        return JsonResponse({'message': message}, status=403)

    files = tasks.extract_files(body)
    if len(files) > settings.MAX_ATTACHMENT_COUNT:
        message = "Too many attachments"
        logger.error(message)
        return JsonResponse({'message': message}, status=403)

    s3 = tasks.make_s3_client()
    metadata_key = get_random_string(50)
    metadata_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.ATTACHMENT_BUCKET,
            'Key': metadata_key,
        },
    )
    chain = celery.chain(
        tasks.submit_comment.s(body),
        tasks.publish_metadata.s(key=metadata_key),
    )
    chain.delay()
    return JsonResponse({
        'status': 'submitted',
        'metadata_url': metadata_url,
    })


@require_http_methods(['GET', 'HEAD'])
def get_federal_agencies(request):
    return lookup_regulations_gov(field='gov_agency',
                                  dependentOnValue='Federal')


@require_http_methods(['GET', 'HEAD'])
def get_gov_agency_types(request):
    return lookup_regulations_gov(field='gov_agency_type')


def lookup_regulations_gov(*args, **kwargs):
    response = requests.get(
        settings.REGS_GOV_API_LOOKUP_URL,
        params=kwargs,
        headers={'X-Api-Key': settings.REGS_GOV_API_KEY}
    )
    if response.status_code == requests.codes.ok:
        return JsonResponse(response.json()['list'], safe=False)
    else:
        logger.error("Failed to lookup regulations.gov: {}",
                     response.status_code, response.text)
        response.raise_for_status()


def validate_attachment(filename, size):
    if size <= 0 or size > settings.ATTACHMENT_MAX_SIZE:
        return False, "Invalid attachment size"
    _, ext = os.path.splitext(filename)
    if ext[1:].lower() not in settings.VALID_ATTACHMENT_EXTENSIONS:
        return False, "Invalid attachment type"
    return True, ""

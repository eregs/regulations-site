import json
import time
import logging

import celery
import requests
from django.conf import settings
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from regulations import tasks

logger = logging.getLogger(__name__)

# TODO: Expire preview URL at commenting deadline
PREVIEW_EXPIRATION_SECONDS = 60 * 60 * 24 * 90


def upload_proxy(request):
    """Create a random key name and a pair of temporary PUT and GET URLS to
    permit attachment uploads and previews from the browser.
    """
    try:
        size = int(request.GET['size'])
        assert 0 < size <= settings.ATTACHMENT_MAX_SIZE
    except (KeyError, ValueError, AssertionError):
        return JsonResponse(
            {'message': 'Invalid attachment size'},
            status=400,
        )
    filename = request.GET['name']
    s3 = tasks.make_s3_client()
    key = get_random_string(50)
    put_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'ContentLength': size,
            'ContentType': request.GET.get('type', 'application/octet-stream'),
            'Bucket': settings.ATTACHMENT_BUCKET,
            'Key': key,
        },
    )
    disposition = 'attachment; filename="{}"'.format(filename)
    get_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'ResponseExpires': time.time() + PREVIEW_EXPIRATION_SECONDS,
            'ResponseContentDisposition': disposition,
            'Bucket': settings.ATTACHMENT_BUCKET,
            'Key': key,
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
    html = tasks.json_to_html(body)
    key = '/'.join([settings.ATTACHMENT_PREVIEW_PREFIX, get_random_string(50)])
    s3 = tasks.make_s3_client()
    with tasks.html_to_pdf(html) as pdf:
        s3.put_object(
            Body=pdf,
            ContentType='application/pdf',
            ContentDisposition='attachment; filename="comment.pdf"',
            Bucket=settings.ATTACHMENT_BUCKET,
            Key=key,
        )
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.ATTACHMENT_BUCKET,
            'Key': key,
        },
    )
    return JsonResponse({'url': url})


@csrf_exempt
@require_http_methods(['POST'])
def submit_comment(request):
    """Submit a comment to the task queue."""
    body = json.loads(request.body.decode('utf-8'))
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

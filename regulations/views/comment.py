import json

import boto3
from django.conf import settings
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from regulations import celery as tasks


def upload_proxy(request):
    """Create a random key name and a temporary upload URL to permit uploads
    from the browser.
    """
    session = boto3.Session(
        aws_access_key_id=settings.ACCESS_KEY_ID,
        aws_secret_access_key=settings.SECRET_ACCESS_KEY,
    )
    s3 = session.client('s3')
    key = get_random_string(50)
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'ContentType': 'application/octet-stream',
            'Bucket': settings.BUCKET,
            'Key': key,
        },
    )
    return JsonResponse({
        'url': url,
        'key': key,
    })


class PrepareCommentView(TemplateView):
    template_name = 'regulations/comment.html'


@csrf_exempt
@require_http_methods(['POST'])
def submit_comment(request):
    """Submit a comment to the task queue."""
    body = json.loads(request.body.decode('utf-8'))
    tasks.submit_comment.delay(body['sections'])
    return JsonResponse({'status': 'submitted'})

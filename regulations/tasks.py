from __future__ import absolute_import

import os
import json
import shutil
import tempfile
import contextlib

import boto3
from botocore.exceptions import ClientError

import requests
from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings

logger = get_task_logger(__name__)


@shared_task(bind=True)
def submit_comment(self, comment, files):
    '''
    Submit the comment to regulations.gov. If unsuccessful, retry the task.
    Number of retries and time between retries is managed by Celery settings.
    '''
    try:
        with assemble_attachments(files) as attachments:
            fields = [
                ('comment_on', settings.COMMENT_DOCUMENT_ID),
                ('general_comment', comment),
            ]
            fields.extend(attachments)
            data = MultipartEncoder(fields)
            response = requests.post(
                settings.REGS_GOV_API_URL,
                data=data,
                headers={
                    'Content-Type': data.content_type,
                    'X-Api-Key': settings.REGS_GOV_API_KEY,
                }
            )
            if response.status_code != requests.codes.created:
                logger.warn("Post to regulations.gov failed: %s %s",
                            response.status_code, response.text)
                self.retry()
            logger.info(response.text)
            return response.json()
    except (ClientError, RequestException):
        logger.exception("submit_comment task failed")
        self.retry()


@shared_task
def publish_metadata(response, key):
    s3 = make_s3_client()
    body = {'trackingNumber': response['trackingNumber']}
    s3.put_object(
        Body=json.dumps(body).encode(),
        Bucket=settings.ATTACHMENT_BUCKET,
        ContentType='application/json',
        Key=key,
    )


@contextlib.contextmanager
def assemble_attachments(files):
    '''
    Assembles a collection of tuples of the form:
    [
        ('uploadedFile', ('fileName1', file-object1),
        ('uploadedFile', ('fileName2', file-object2),
        ...
    ]
    for POSTing as a multipart/form-data upload.
    On context exit, the file objects are closed and the locally
    downloaded files are deleted.
    '''
    try:
        path = tempfile.mkdtemp()
        attachments = [
            ('uploadedFile', (file_['name'],
                              fetch_file(path, file_['key'], file_['name'])))
            for file_ in files
        ]
        yield attachments
    finally:
        for file_ in attachments:
            file_[1][1].close()
        shutil.rmtree(path)


def fetch_file(path, key, name):
    '''
    Returns a file object corresponding to a local file stored at ``path+name``
    whose content is downloaded from S3 where it is stored under ``key``

    '''
    s3 = make_s3_client()
    dest = os.path.join(path, name)
    s3.download_file(settings.ATTACHMENT_BUCKET, key, dest)
    return open(dest, "rb")


def make_s3_client():
    session = boto3.Session(
        aws_access_key_id=settings.ATTACHMENT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.ATTACHMENT_SECRET_ACCESS_KEY,
    )
    return session.client('s3')

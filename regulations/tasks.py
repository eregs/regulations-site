from __future__ import absolute_import

import os
import json
import shutil
import tempfile
import contextlib

import boto3

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.template import loader

logger = get_task_logger(__name__)

# The following limits are specified by the regulations.gov API
# They are not available as a queryable endpoint
MAX_ATTACHMENT_COUNT = 10
VALID_ATTACHMENT_EXTENSIONS = set([
    "bmp", "doc", "xls", "pdf", "gif", "htm", "html", "jpg", "jpeg",
    "png", "ppt", "rtf", "sgml", "tiff", "tif", "txt", "wpd", "xml",
    "docx", "xlsx", "pptx"])


@shared_task
def submit_comment(body):
    comment = build_comment(body)
    files = extract_files(body)
    valid, message = validate_attachments(files)
    if not valid:
        logger.error(message)
        return
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
        response.raise_for_status()
        logger.info(response.text)
        return response.json()


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


def build_comment(body):
    return loader.render_to_string('regulations/comment.md', body)


def extract_files(body):
    '''
    Extracts the files that are to be attached to the comment.
    Returns a collection of dicts where for each dict:
        - dict['key'] specifies the file to be attached from S3
        - dict['name'] specifies the name under which the file is to be
          attached.
    '''
    return [
        file
        for section in body.get('sections', [])
        for file in section.get('files', [])
    ]


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


def validate_attachments(files):
    if len(files) > MAX_ATTACHMENT_COUNT:
        return False, "Too many attachments"
    for file_ in files:
        _, ext = os.path.splitext(file_['name'])
        if ext[1:].lower() not in VALID_ATTACHMENT_EXTENSIONS:
            return False, "Invalid attachment type"
    return True, ""

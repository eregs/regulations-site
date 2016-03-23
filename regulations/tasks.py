from __future__ import absolute_import

import os
import shutil
import tempfile
import contextlib

import boto3
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from celery import shared_task
from django.conf import settings


@shared_task
def submit_comment(comment):
    with AttachmentSet(comment) as attachments:
        fields = [
            ("comment_on", comment["document_id"]),
            ("general_comment", comment["comment"]),
        ]
        fields.extend(attachments)
        data = MultipartEncoder(fields)
        response = requests.post(
            settings.REGS_API_URL,
            data=data,
            headers={
                "Content-Type": data.content_type,
                "X-Api-Key": settings.REGS_API_KEY
            }
        )
        print(response.text)


@contextlib.contextmanager
def AttachmentSet(comment):
    '''
    Assembles a collection of tuples of the form:
    [
        ('uploadedFile', ('fileName1', file-object1),
        ('uploadedFile', ('fileName2', file-object2),
        ...
    ]
    for POSTing as a multipart/form-data upload.
    comment['files'] is a collection of dicts where for each dict:
        - dict['key'] specifies the file to be attached from S3
        - dict['name'] specifies the name under which the file is to be
          attached.
    On context exit, the file objects are closed and the locally
    downloaded files are deleted.
    '''
    try:
        path = tempfile.mkdtemp()
        attachments = [
            ('uploadedFile', (file_['name'],
                              fetch_file(path, file_['key'], file_['name'])))
            for file_ in comment.get('files', [])
        ]
        yield attachments
    finally:
        for file_ in attachments:
            attachments[1][1].close()
        shutil.rmtree(path)


def fetch_file(path, key, name):
    '''
    Returns a file object corresponding to a local file stored at ``path+name``
    whose content is downloaded from S3 where it is stored under ``key``

    '''
    session = boto3.Session(
        aws_access_key_id=settings.ATTACHMENT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.ATTACHMENT_SECRET_ACCESS_KEY,
    )
    s3 = session.client('s3')
    dest = os.path.join(path, name)
    s3.download_file(settings.ATTACHMENT_BUCKET, key, dest)
    return open(dest, "rb")

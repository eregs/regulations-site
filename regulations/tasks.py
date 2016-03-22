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
from django.template import loader


@shared_task
def submit_comment(body):
    comment = build_comment(body)
    files = extract_files(body)
    with TemporaryDirectory() as path:
        fields = [
            ('comment_on', body['doc_number']),
            ('general_comment', comment),
        ]
        files = [
            (
                'uploadedFile',
                (file['name'], fetch_file(path, file['key'], file['name'])),
            )
            for file in files
        ]
        fields.extend(files)
        data = MultipartEncoder(fields)
        requests.post(
            settings.REGS_API_URL,
            data=data,
            headers={
                'Content-Type': data.content_type,
                'X-Api-Key': settings.REGS_API_KEY,
            }
        )


def build_comment(body):
    return loader.render_to_string('regulations/comment.md', body)


def extract_files(body):
    return [
        file
        for section in body.get('sections', [])
        for file in section.get('files', [])
    ]


@contextlib.contextmanager
def TemporaryDirectory(*args, **kwargs):
    try:
        path = tempfile.mkdtemp(*args, **kwargs)
        yield path
    finally:
        shutil.rmtree(path)


def fetch_file(path, key, name):
    session = boto3.Session(
        aws_access_key_id=settings.ATTACHMENT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.ATTACHMENT_SECRET_ACCESS_KEY,
    )
    s3 = session.client('s3')
    dest = os.path.join(path, name)
    s3.download_file(settings.ATTACHMENT_BUCKET, key, dest)
    return dest

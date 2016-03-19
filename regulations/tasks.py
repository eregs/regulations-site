from __future__ import absolute_import

import os
import shutil
import tempfile
import contextlib

import boto3
import requests
from celery import shared_task
from django.conf import settings


@shared_task
def submit_comment(sections):
    with TemporaryDirectory() as path:
        files = [
            fetch_file(path, file['key'], file['name'])
            for section in sections
            for file in section.get('files', [])
        ]
        comment = build_comment(sections)
        requests.post(
            settings.REGS_API_URL,
            data={
                'comment': comment,
            },
            files=(
                ('file', open(file, 'rb'))
                for file in files
            ),
        )


@contextlib.contextmanager
def TemporaryDirectory(*args, **kwargs):
    try:
        path = tempfile.mkdtemp(*args, **kwargs)
        yield path
    finally:
        shutil.rmtree(path)


def fetch_file(path, key, name):
    session = boto3.Session(
        aws_access_key_id=settings.ACCESS_KEY_ID,
        aws_secret_access_key=settings.SECRET_ACCESS_KEY,
    )
    s3 = session.client('s3')
    dest = os.path.join(path, name)
    s3.download_file(settings.BUCKET, key, dest)
    return dest


def build_comment(sections):
    return '\n\n'.join([
        '# {}\n{}'.format(section['id'], section['comment'])
        for section in sections
    ])

from __future__ import absolute_import

import os
import json
import shutil
import tempfile
import contextlib
import subprocess

import six
import markdown2

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

import requests
from requests.exceptions import RequestException
from requests_toolbelt.multipart.encoder import MultipartEncoder

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from django.conf import settings
from django.template import loader

from regulations.models import FailedCommentSubmission
logger = get_task_logger(__name__)


@shared_task(bind=True)
def submit_comment(self, body):
    '''
    Submit the comment to regulations.gov. If unsuccessful, retry the task.
    Number of retries and time between retries is managed by Celery settings.
    The main comment is converted to a PDF and added as an attachment; the
    'general_comment' field refers to this attachment.

    :param body: dict of fields and values to be posted to regulations.gov
    '''
    sections = body.get('assembled_comment', [])
    try:
        html = json_to_html(sections)
        files = extract_files(sections)
        try:
            with html_to_pdf(html) as comment, \
                    build_attachments(files) as attachments:
                fields = [
                    ('comment_on', settings.COMMENT_DOCUMENT_ID),
                    # TODO: Ensure this name is unique
                    ('uploadedFile', ('comment.pdf', comment)),
                    ('general_comment', 'See attached comment.pdf'),
                ]

                # Add other submitted fields
                fields.extend([
                    (name, value)
                    for name, value in six.iteritems(body)
                    if name != 'assembled_comment'
                ])
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
                    raise self.retry()
                logger.info(response.text)
                return response.json()
        except (RequestException, ClientError):
            logger.exception("Unable to submit comment")
            raise self.retry()
    except MaxRetriesExceededError:
        message = "Exceeded retries, saving failed submission"
        logger.error(message)
        FailedCommentSubmission.objects.create(body=json.dumps(body))
        return {'message': message, 'trackingNumber': None}


@shared_task
def publish_tracking_number(response, key):
    s3 = make_s3_client()
    body = {'trackingNumber': response['trackingNumber']}
    s3.put_object(
        Body=json.dumps(body).encode(),
        Bucket=settings.ATTACHMENT_BUCKET,
        ContentType='application/json',
        Key=key,
    )


def json_to_html(sections):
    md = loader.render_to_string(
        'regulations/comment.md', {'sections': sections})
    return markdown2.markdown(md)


@contextlib.contextmanager
def html_to_pdf(html):
    try:
        path = tempfile.mkdtemp()
        html_path = os.path.join(path, 'document.html')
        pdf_path = os.path.join(path, 'document.pdf')
        with open(html_path, 'w') as fp:
            fp.write(html)
        subprocess.check_output(
            [settings.WKHTMLTOPDF_PATH, html_path, pdf_path])
        with open(pdf_path, 'rb') as pdf_file:
            yield pdf_file
    finally:
        shutil.rmtree(path)


@contextlib.contextmanager
def build_attachments(files):
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
    return session.client('s3', config=Config(signature_version='s3v4'))


def extract_files(sections):
    '''
    Extracts the files that are to be attached to the comment.
    Returns a collection of dicts where for each dict:
        - dict['key'] specifies the file to be attached from S3
        - dict['name'] specifies the name under which the file is to be
          attached.
    '''
    return [
        file
        for section in sections
        for file in section.get('files', [])
    ]

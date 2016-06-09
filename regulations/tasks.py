from __future__ import absolute_import

import os
import json
import codecs
import shutil
import tempfile
import contextlib
import subprocess   # nosec - see usage below
import collections

import boto3
from botocore.client import Config

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from django.conf import settings
from django.contrib.staticfiles import finders
from django.template import loader
from django.utils.crypto import get_random_string

from regulations.models import FailedCommentSubmission
logger = get_task_logger(__name__)


@shared_task(bind=True, acks_late=True)
def submit_comment(self, comments, form_data, metadata_url):
    '''
    Submit the comment to regulations.gov. If unsuccessful, retry the task.
    Number of retries and time between retries is managed by Celery settings.
    The main comment is converted to a PDF and added as an attachment; the
    'general_comment' field refers to this attachment.

    :param comments: List of sectional comments
    :param form_data: Dict of fields accepted by regulations.gov
    :param metadata_url: SignedUrl for comment metadata

    :return: On success: {"trackingNumber": "...", "pdfUrl": "..."}
             On failure: raises "retry" exception
             On multiple failures: {"error": "Message"}
    '''
    try:
        html = json_to_html(comments)
        files = extract_files(comments)
        with html_to_pdf(html) as comment_pdf, \
                build_attachments(files) as attachments:
            document_number = get_document_number(comments)
            pdf_url = cache_pdf(comment_pdf, document_number, metadata_url)

            # Restore file position changed by cache_pdf
            comment_pdf.seek(0)

            data = build_multipart_encoded(
                form_data, comment_pdf, attachments)
            response = post_submission(data)
            if response.status_code != requests.codes.created:
                logger.warn("Post to regulations.gov failed: %s %s",
                            response.status_code, response.text)
                raise self.retry()
            logger.info(response.text)
            data = response.json()
            return {
                'trackingNumber': data['trackingNumber'],
                'pdfUrl': pdf_url.url,
            }
    except Exception:   # We want to catch _any_ exception
        logger.exception("Unable to submit comment")
        try:
            raise self.retry()
        except MaxRetriesExceededError:
            message = "Exceeded retries, saving failed submission"
            logger.error(message)
            save_failed_submission(
                json.dumps({'comments': comments, 'form_data': form_data})
            )
            return {'error': message}


@shared_task(acks_late=True)
def publish_tracking_number(response, metadata_url):
    """Write the tracking number to S3. Not ideal if this fails, but the
    comment will have been taken care of already, so no need for additional
    safety checks"""
    s3_client.put_object(
        Body=json.dumps(response).encode(),
        Bucket=settings.ATTACHMENT_BUCKET,
        ContentType='application/json',
        Key=metadata_url.key,
    )


def json_to_html(sections, mark_as_draft=False):
    """
    Render the comment as HTML

    :param sections: The section-by-section comments
    :param mark_as_draft: Indicates if the HTML is to be marked as DRAFT
    """
    return loader.render_to_string(
        'regulations/comment.html',
        {'sections': sections, 'mark_as_draft': mark_as_draft}
    )


@contextlib.contextmanager
def html_to_pdf(html):
    try:
        path = tempfile.mkdtemp()
        html_path = os.path.join(path, 'document.html')
        pdf_path = os.path.join(path, 'document.pdf')
        with codecs.open(html_path, 'w', 'utf-8') as fp:
            fp.write(html)
        # Safe because: user provides no input
        subprocess.check_output([   # nosec
            settings.WKHTMLTOPDF_PATH,
            '--user-style-sheet',
            finders.find('regulations/css/style.css'),
            html_path,
            pdf_path,
        ])
        with open(pdf_path, 'rb') as pdf_file:
            yield pdf_file
    finally:
        shutil.rmtree(path)


def cache_pdf(pdf, document_number, metadata_url):
    """Update submission metadata and cache comment PDF."""
    url = SignedUrl.generate()
    content_disposition = generate_content_disposition(document_number,
                                                       draft=False)
    s3_client.put_object(
        Body=json.dumps({'pdfUrl': metadata_url.url}),
        Bucket=settings.ATTACHMENT_BUCKET,
        Key=metadata_url.key,
    )
    s3_client.put_object(
        Body=pdf,
        ContentType='application/pdf',
        ContentDisposition=content_disposition,
        Bucket=settings.ATTACHMENT_BUCKET,
        Key=url.key,
    )
    return url


def generate_content_disposition(document_number, draft=False):
    return 'attachment; filename="{}comment_{}.pdf"'.format(
        "DRAFT_" if draft else "",
        document_number
    )


def get_document_number(comments):
    """ Get the FR document number for the notice against which the comments
    are being submitted
    """
    return comments[0]['docId']


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
    attachments = []
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
    dest = os.path.join(path, name)
    s3_client.download_file(settings.ATTACHMENT_BUCKET, key, dest)
    return open(dest, "rb")


def make_s3_client():
    session = boto3.Session(
        aws_access_key_id=settings.ATTACHMENT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.ATTACHMENT_SECRET_ACCESS_KEY,
    )
    return session.client('s3', config=Config(signature_version='s3v4'))


s3_client = make_s3_client()


class SignedUrl(collections.namedtuple('SignedUrl', ['key', 'url'])):
    @classmethod
    def generate(cls, key=None, method='get_object', params=None):
        key = key or get_random_string(50)
        params = params or {}
        params.update({'Bucket': settings.ATTACHMENT_BUCKET, 'Key': key})
        url = s3_client.generate_presigned_url(
            ClientMethod=method,
            Params=params,
        )
        return cls(key, url)


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


def build_multipart_encoded(form_data, comment_pdf, attachments):
    """ Build a MultiPartEncoded payload from the extra body fields,
        the main comment PDF and the set of attachments
    """
    fields = [
        ('comment_on', settings.COMMENT_DOCUMENT_ID),
        # TODO: Ensure this name is unique
        ('uploadedFile', ('comment.pdf', comment_pdf)),
        ('general_comment', 'See attached comment.pdf'),
    ]

    # Add other submitted fields
    fields.extend(form_data.items())
    fields.extend(attachments)
    return MultipartEncoder(fields)


def save_failed_submission(body):
    FailedCommentSubmission.objects.create(body=body)


def post_submission(data):
    return requests.post(
        settings.REGS_GOV_API_URL,
        data=data,
        headers={
            'Content-Type': data.content_type,
            'X-Api-Key': settings.REGS_GOV_API_KEY,
        }
    )

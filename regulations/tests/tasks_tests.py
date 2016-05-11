import json
import mock
import six

from nose.tools import *  # noqa
from requests.exceptions import RequestException
from celery.exceptions import Retry, MaxRetriesExceededError

from django.conf import settings
from django.test import TestCase, override_settings

from regulations.tasks import submit_comment, cache_pdf, SignedUrl
from regulations.models import FailedCommentSubmission


@mock.patch('regulations.tasks.submit_comment.retry')
@mock.patch('regulations.tasks.post_submission')
@mock.patch('regulations.tasks.html_to_pdf')
@mock.patch('regulations.tasks.cache_pdf')
@override_settings(
    ATTACHMENT_BUCKET='test-bucket',
    ATTACHMENT_ACCESS_KEY_ID='test-access-key',
    ATTACHMENT_SECRET_ACCESS_KEY='test-secret-key',
    ATTACHMENT_MAX_SIZE=42,
    REGS_GOV_API_URL='test-url',
    REGS_GOV_API_KEY='test-key',
)
class TestSubmitComment(TestCase):

    def setUp(self):
        self.file_handle = six.BytesIO(b"some-byte-content")
        self.comments = [
            {"id": "A1", "comment": "A simple comment", "files": []},
            {"id": "A5", "comment": "Another comment", "files": []}
        ]
        self.form = {}
        self.meta = SignedUrl('meta', 'https://s3.amazonaws.com/bucket/meta')

    def tearDown(self):
        FailedCommentSubmission.objects.all().delete()

    def test_submit_comment(self, cache_pdf, html_to_pdf, post_submission,
                            retry):
        cache_pdf.return_value = SignedUrl(
            'pdf', 'https://s3.amazonaws.com/bucket/pdf')
        html_to_pdf.return_value.__enter__.return_value = self.file_handle

        expected_result = {'trackingNumber': 'some-tracking-number'}
        post_submission.return_value.status_code = 201
        post_submission.return_value.json.return_value = expected_result

        result = submit_comment(self.comments, self.form, self.meta)

        self.assertEqual(
            result,
            {
                'trackingNumber': 'some-tracking-number',
                'pdfUrl': cache_pdf.return_value.url
            },
        )
        self.assertFalse(FailedCommentSubmission.objects.all(),
                         "No submissions saved")

    def test_failed_submit_raises_retry(self, cache_pdf, html_to_pdf,
                                        post_submission, retry):
        cache_pdf.return_value = SignedUrl(
            'pdf', 'https://s3.amazonaws.com/bucket/pdf')
        html_to_pdf.return_value.__enter__.return_value = self.file_handle

        post_submission.side_effect = RequestException

        retry.return_value = Retry()

        with self.assertRaises(Retry):
            submit_comment(self.comments, self.form, self.meta)
        self.assertFalse(FailedCommentSubmission.objects.all(),
                         "No submissions saved")

    def test_failed_submit_maximum_retries(self, cache_pdf, html_to_pdf,
                                           post_submission, retry):
        cache_pdf.return_value = SignedUrl(
            'pdf', 'https://s3.amazonaws.com/bucket/pdf')
        html_to_pdf.return_value.__enter__.return_value = self.file_handle

        post_submission.side_effect = RequestException

        retry.return_value = MaxRetriesExceededError()

        submit_comment(self.comments, self.form, self.meta)
        saved_submission = FailedCommentSubmission.objects.all()[0]
        self.assertEqual(
            json.dumps({
                'comments': self.comments,
                'form_data': self.form,
            }),
            saved_submission.body,
        )


class TestHelpers(TestCase):

    @mock.patch('regulations.tasks.SignedUrl.generate')
    @mock.patch('regulations.tasks.s3_client')
    def test_cache_pdf(self, s3_client, url_generate):
        meta = SignedUrl('meta', 'https://s3.amazonaws.com/bucket/meta')
        url_generate.return_value = SignedUrl(
            'pdf', 'https://s3.amazonaws.com/bucket/pdf')
        url = cache_pdf('content', meta)
        assert_equal(url, url_generate.return_value)
        s3_client.put_object.assert_any_call(
            Body=json.dumps({'pdfUrl': meta.url}),
            Bucket=settings.ATTACHMENT_BUCKET,
            Key=meta.key,
        )
        s3_client.put_object.assert_any_call(
            Body='content',
            Bucket=settings.ATTACHMENT_BUCKET,
            Key=url.key,
        )

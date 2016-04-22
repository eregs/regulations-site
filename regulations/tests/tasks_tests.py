import json
import mock
import six

from celery.exceptions import Retry, MaxRetriesExceededError
from requests.exceptions import RequestException
from django.test import SimpleTestCase, override_settings

from regulations.tasks import submit_comment


@mock.patch('regulations.tasks.save_failed_submission')
@mock.patch('regulations.tasks.submit_comment.retry')
@mock.patch('regulations.tasks.post_submission')
@mock.patch('regulations.tasks.html_to_pdf')
@override_settings(
    ATTACHMENT_BUCKET='test-bucket',
    ATTACHMENT_ACCESS_KEY_ID='test-access-key',
    ATTACHMENT_SECRET_ACCESS_KEY='test-secret-key',
    ATTACHMENT_MAX_SIZE=42,
    REGS_GOV_API_URL='test-url',
    REGS_GOV_API_KEY='test-key',
)
class TestSubmitComment(SimpleTestCase):

    def setUp(self):
        self.file_handle = six.BytesIO("some-content")
        self.submission = {'assembled_comment': [
            {"id": "A1", "comment": "A simple comment", "files": []},
            {"id": "A5", "comment": "Another comment", "files": []}
        ]}

    def test_submit_comment(self, html_to_pdf, post_submission, retry,
                            save_failed_submission):
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=self.file_handle)

        expected_result = {'tracking_number': 'some-tracking-number'}
        post_submission.return_value.status_code = 201
        post_submission.return_value.json.return_value = expected_result

        result = submit_comment(self.submission)

        self.assertEqual(result, expected_result)

    def test_failed_submit_raises_retry(self, html_to_pdf, post_submission,
                                        retry, save_failed_submission):
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=self.file_handle)

        post_submission.side_effect = [RequestException]

        retry.return_value = Retry()

        with self.assertRaises(Retry):
            submit_comment(self.submission)

    def test_failed_submit_maximum_retries(self, html_to_pdf, post_submission,
                                           retry, save_failed_submission):
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=self.file_handle)

        post_submission.side_effect = [RequestException]

        retry.return_value = MaxRetriesExceededError()

        submit_comment(self.submission)
        save_failed_submission.assert_called_with(json.dumps(self.submission))

import json
import mock
import six

from celery.exceptions import Retry, MaxRetriesExceededError
from requests.exceptions import RequestException
from django.test import SimpleTestCase, override_settings

from regulations.tasks import submit_comment


@mock.patch('regulations.tasks.save_failed_submission')
@mock.patch('regulations.tasks.submit_comment.retry')
@mock.patch('requests.post')
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

    def test_submit_comment(self, html_to_pdf, post, retry,
                            save_failed_submission):
        file_handle = six.BytesIO("foobar")
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=file_handle)

        expected_result = {'tracking_number': '133321'}
        post.return_value.status_code = 201
        post.return_value.json.return_value = expected_result

        body = {'assembled_comment': {'sections': []}}
        result = submit_comment(body)

        self.assertEqual(result, expected_result)

    def test_failed_submit_raises_retry(self, html_to_pdf, post, retry,
                                        save_failed_submission):
        file_handle = six.BytesIO("foobar")
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=file_handle)

        post.side_effect = [RequestException]

        retry.return_value = Retry()

        body = {'assembled_comment': {'sections': []}}
        with self.assertRaises(Retry):
            submit_comment(body)

    def test_failed_submit_maximum_retries(self, html_to_pdf, post, retry,
                                           save_failed_submission):
        file_handle = six.BytesIO("foobar")
        html_to_pdf.return_value.__enter__ = mock.Mock(
            return_value=file_handle)

        post.side_effect = [RequestException]

        retry.return_value = MaxRetriesExceededError()

        body = {'assembled_comment': {'sections': []}}
        submit_comment(body)
        save_failed_submission.assert_called_with(json.dumps(body))

import json
import mock

from django.test import SimpleTestCase, override_settings

from regulations.views import comment


@override_settings(
    ATTACHMENT_BUCKET='test-bucket',
    ATTACHMENT_ACCESS_KEY_ID='test-access-key',
    ATTACHMENT_SECRET_ACCESS_KEY='test-secret-key',
    ATTACHMENT_MAX_SIZE=42,
)
class TestUploadProxy(SimpleTestCase):

    @mock.patch('time.time')
    @mock.patch('regulations.tasks.s3_client')
    @mock.patch('regulations.tasks.get_random_string')
    def test_get_url(self, get_random, mock_client, mock_time):
        generate_presigned = mock_client.generate_presigned_url
        generate_presigned.side_effect = ['first-url', 'second-url']
        get_random.return_value = 'not-so-random'
        mock_time.return_value = 123
        resp = self.client.get('/comments/attachment?size=42&name=foo.pdf')
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content.decode())
        generate_presigned.assert_any_call(
            ClientMethod='put_object',
            Params={
                'ContentLength': 42,
                'ContentType': 'application/octet-stream',
                'Bucket': 'test-bucket',
                'Key': get_random.return_value,
                'Metadata': {'name': 'foo.pdf'}
            },
        )
        generate_presigned.assert_any_call(
            ClientMethod='get_object',
            Params={
                'ResponseExpires': 123 + comment.PREVIEW_EXPIRATION_SECONDS,
                'ResponseContentDisposition': 'attachment; filename="foo.pdf"',
                'Bucket': 'test-bucket',
                'Key': get_random.return_value,
            },
        )
        self.assertEqual(body['key'], get_random.return_value)
        self.assertEqual(body['urls']['put'], 'first-url')
        self.assertEqual(body['urls']['get'], 'second-url')

    def test_get_url_empty(self):
        resp = self.client.get('/comments/attachment?size=0&name=foo.pdf')
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.content.decode())
        self.assertEqual(body['message'], 'Invalid attachment size')

    def test_get_url_over_limit(self):
        resp = self.client.get('/comments/attachment?size=43&name=foo.pdf')
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.content.decode())
        self.assertEqual(body['message'], 'Invalid attachment size')

    def test_get_url_invalid_extension(self):
        resp = self.client.get('/comments/attachment?size=42&name=foo.exe')
        self.assertEqual(resp.status_code, 400)
        body = json.loads(resp.content.decode())
        self.assertEqual(body['message'], 'Invalid attachment type')

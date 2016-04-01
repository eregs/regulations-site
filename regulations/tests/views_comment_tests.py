import json
import mock

from django.test import SimpleTestCase, override_settings


@override_settings(
    ATTACHMENT_BUCKET='test-bucket',
    ATTACHMENT_ACCESS_KEY_ID='test-access-key',
    ATTACHMENT_SECRET_ACCESS_KEY='test-secret-key',
    ATTACHMENT_MAX_SIZE=42,
)
class TestUploadProxy(SimpleTestCase):

    @mock.patch('regulations.tasks.boto3.Session')
    @mock.patch('regulations.views.comment.get_random_string')
    def test_get_url(self, get_random, session):
        client = session.return_value.client
        generate_presigned = client.return_value.generate_presigned_url
        generate_presigned.return_value = 'test-url'
        get_random.return_value = 'not-so-random'
        resp = self.client.get('/comments/attachment?size=42&name=foo.pdf')
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content.decode())
        generate_presigned.assert_called_with(
            ClientMethod='put_object',
            Params={
                'ContentLength': 42,
                'ContentType': 'application/octet-stream',
                'Bucket': 'test-bucket',
                'Key': get_random.return_value,
                'Metadata': {'name': 'foo.pdf'}
            },
        )
        self.assertEqual(body['key'], get_random.return_value)
        self.assertEqual(body['url'], generate_presigned.return_value)

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

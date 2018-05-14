import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Set CORS rules on the Notice and Comment attachment bucket'

    def handle(self, *args, **options):
        hosts = settings.ALLOWED_HOSTS
        origins = ['http://' + host for host in hosts]
        origins = origins + ['https://' + host for host in hosts]

        session = boto3.Session(
            aws_access_key_id=settings.ATTACHMENT_ACCESS_KEY_ID,
            aws_secret_access_key=settings.ATTACHMENT_SECRET_ACCESS_KEY,
        )
        s3 = session.client('s3')

        s3.put_bucket_cors(
            Bucket=settings.ATTACHMENT_BUCKET,
            CORSConfiguration={
                'CORSRules': [
                    {
                        'AllowedMethods': ['GET', 'PUT'],
                        'AllowedOrigins': origins or ['*'],
                        'AllowedHeaders': ['*'],
                    },
                ],
            },
        )

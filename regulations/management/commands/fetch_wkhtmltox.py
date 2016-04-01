import os
import subprocess

from django.core.management.base import BaseCommand


BIN_PATH = (
    'http://download.gna.org', 'wkhtmltopdf', '0.12', '0.12.3',
    'wkhtmltox-0.12.3_linux-generic-amd64.tar.xz',
)


class Command(BaseCommand):
    help = 'Fetch wkhtmltox binary'

    def handle(self, **options):
        subprocess.check_call(['wget', '-r', os.path.join(*BIN_PATH)])
        subprocess.check_call(['tar', 'xzvf', BIN_PATH[-1]])

import platform
import subprocess

from django.core.management.base import BaseCommand, CommandError


BIN_PATH = (
    'http://download.gna.org', 'wkhtmltopdf', '0.12', '0.12.3',
    'wkhtmltox-0.12.3_linux-generic-amd64.tar.xz',
)


class Command(BaseCommand):
    help = 'Fetch wkhtmltox binary'

    def handle(self, **options):
        if platform.system() != 'Linux':
            raise CommandError(
                'The `wkhtmltox` command only handles linux; to install on '
                'another platform, see http://wkhtmltopdf.org/downloads.html.'
            )
        subprocess.check_call([
            'wget', '-O', BIN_PATH[-1], '/'.join(BIN_PATH)])
        subprocess.check_call(['tar', 'xvf', BIN_PATH[-1]])

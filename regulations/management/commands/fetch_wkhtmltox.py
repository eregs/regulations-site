import platform
import os.path
import subprocess   # nosec - see usage below

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


BIN_PATH = (
    'http://download.gna.org', 'wkhtmltopdf', '0.12', '0.12.3',
    'wkhtmltox-0.12.3_linux-generic-amd64.tar.xz',
)


class Command(BaseCommand):
    help = 'Fetch wkhtmltox binary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true', dest='force', default=False,
            help="Download the binary even if it's present")

    def handle(self, **options):
        if platform.system() != 'Linux':
            raise CommandError(
                'The `wkhtmltox` command only handles linux; to install on '
                'another platform, see http://wkhtmltopdf.org/downloads.html.'
            )

        path = settings.WKHTMLTOPDF_PATH
        if path and os.path.exists(path) and not options['force']:
            message = ("WKHTMLTOPDF already exists: {}\n"
                       "Skipping. Use the --force flag if necessary.")
            self.stderr.write(self.style.NOTICE(
                message.format(settings.WKHTMLTOPDF_PATH)))
        else:
            # Safe because: we're not passing user input into these processes
            subprocess.check_call([     # nosec
                'wget', '-O', BIN_PATH[-1], '/'.join(BIN_PATH)])
            subprocess.check_call(['tar', 'xvf', BIN_PATH[-1]])     # nosec

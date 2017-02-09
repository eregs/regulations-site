import codecs
import os
import shutil
import subprocess   # nosec - see usage below

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.staticfiles.finders import get_finders
from django.contrib.staticfiles.storage import StaticFilesStorage


"""
This command compiles the frontend for regulations-site after using the Django
``collectstatic`` command to override specific files, and places the output in
a directory named ``compiled`` at the root level of the project.

For example, the atf-eregs project uses ``regulations-site`` as a library and
overrides the contents of the
``regulations/static/regulations/css/less/mixins.less`` file. The
``atf_eregs/regulations/static/regulations/css/less/mixins.less`` file will be
copied over the base file from ``regulations-site`` and put into a build
directory by ``collectstatic``, and then the frontend build commands are run,
and the results are copied into ``compiled``, which can then be used as the
static directory for the CSS, font, JavaScript, and image assets.

"""


class Command(BaseCommand):
    help = 'Build the frontend, including local overrides.'
    BUILD_DIR = "./frontend_build"
    TARGET_DIR = "./compiled/regulations"

    def add_arguments(self, parser):
        parser.add_argument('--no-install', dest='install',
                            action='store_false')
        parser.set_defaults(install=True)

    def remove_dirs(self):
        """Remove existing output dirs"""
        if os.path.exists(self.TARGET_DIR):
            shutil.rmtree(self.TARGET_DIR)
        # Delete everything in BUILD_DIR except node_modules, which we use for
        # caching the downloaded node libraries
        if os.path.exists(self.BUILD_DIR):
            all_content = [os.path.join(self.BUILD_DIR, f)
                           for f in os.listdir(self.BUILD_DIR)]
            files = filter(os.path.isfile, all_content)
            dirs = filter(os.path.isdir, all_content)
            for f in files:
                os.remove(f)
            for d in dirs:
                if d != os.path.join(self.BUILD_DIR, 'node_modules'):
                    shutil.rmtree(d)
        else:
            os.mkdir(self.BUILD_DIR)

    def create_configs(self):
        for config_file in ('Gruntfile.js', 'package.json', '.babelrc'):
            os.rename(os.path.join(self.BUILD_DIR, 'static', 'config',
                                   config_file),
                      os.path.join(self.BUILD_DIR, config_file))
        with codecs.open("%s/config.json" % self.BUILD_DIR, "w",
                         encoding="utf-8") as f:
            f.write('{"frontEndPath": "static/regulations"}')

    def _input_files(self):
        """Fetch all of the static files from the installed apps. Yield them
        as pairs of (path, file)"""
        files_seen = set()
        pairs = (pr for finder in get_finders() for pr in finder.list([]))
        for path, storage in pairs:
            # Prefix the relative path if the source storage contains it
            if getattr(storage, 'prefix', None):
                prefixed_path = os.path.join(storage.prefix, path)
            else:
                prefixed_path = path
            if prefixed_path in files_seen:
                self.stdout.write(
                    "Using override for {}\n".format(prefixed_path))
            else:
                files_seen.add(prefixed_path)
                with storage.open(path) as source_file:
                    yield (prefixed_path, source_file)

    def collect_files(self):
        """Find and write static files. Along the way ignore the "compiled"
        directory, if present"""
        write_storage = StaticFilesStorage(self.BUILD_DIR + "/static/")
        original_dirs = settings.STATICFILES_DIRS
        settings.STATICFILES_DIRS = [s for s in original_dirs
                                     if s != 'compiled']
        for prefixed_path, source_file in self._input_files():
            write_storage.save(prefixed_path, source_file)
        settings.STATICFILES_DIRS = original_dirs

    def build_frontend(self, install=True, dev=False):
        """Shell out to npm for building the frontend files"""
        cmd = 'build-dev' if dev else 'build-dist'
        # Safe because: we're not passing user input into these processes
        if install:
            subprocess.check_call(  # nosec
                ['npm', 'install'], cwd=self.BUILD_DIR)
        subprocess.check_call(['grunt', cmd], cwd=self.BUILD_DIR)   # nosec

    def cleanup(self):
        shutil.copytree("%s/static/regulations" % self.BUILD_DIR,
                        self.TARGET_DIR)

    def handle(self, **options):
        self.remove_dirs()
        self.collect_files()
        self.create_configs()
        self.build_frontend(install=options['install'], dev=settings.JS_DEBUG)
        self.cleanup()

import codecs
import regulations
import os
import shutil
import subprocess

from django.core.management.base import BaseCommand

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

    def find_regulations_directory(self):
        child = regulations.__file__
        child_dir = os.path.split(child)[0]
        return os.path.split(child_dir)[0]

    def remove_dirs(self):
        """Remove existing output dirs"""
        for dirpath in (self.BUILD_DIR, self.TARGET_DIR):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)

    def copy_configs(self):
        """Copy over configs from regulations"""
        regulations_directory = self.find_regulations_directory()
        frontend_files = (
            "package.json",
            "bower.json",
            "Gruntfile.js",
            ".eslintrc"
        )
        for f_file in frontend_files:
            source = "%s/%s" % (regulations_directory, f_file)
            shutil.copy(source, "%s/" % self.BUILD_DIR)
        with codecs.open("%s/config.json" % self.BUILD_DIR, "w",
                         encoding="utf-8") as f:
            f.write('{"frontEndPath": "static/regulations"}')

    def collect_files(self):
        """Fetch all of the static files from the installed apps -- put them
        into a specific directory"""
        os.environ["TMPDIR"] = self.BUILD_DIR
        subprocess.call(["python", "manage.py", "collectstatic", "--noinput"])

    def build_frontend(self):
        """Shell out to npm for building the frontend files"""
        os.chdir(self.BUILD_DIR)
        subprocess.call(["npm", "install", "grunt-cli", "bower"])
        subprocess.call(["npm", "install"])
        os.chdir("..")

    def cleanup(self):
        shutil.copytree("%s/static/regulations" % self.BUILD_DIR,
                        self.TARGET_DIR)

    def handle(self, *args, **options):
        self.remove_dirs()
        self.copy_configs()
        self.collect_files()
        self.build_frontend()
        self.cleanup()

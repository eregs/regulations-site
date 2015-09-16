import codecs
import distutils
import regulations
import os
import shutil
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

"""
This command compiles the frontend for regulations-site after using the Django
``collectstatic`` command to override specific files, and places the output in a
directory named ``compiled`` at the root level of the project.

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

    def find_regulations_directory(self):
        child = regulations.__file__
        child_dir = os.path.split(child)[0]
        return os.path.split(child_dir)[0]

    def run_collectstatic(self):
        subprocess.call(["python", "manage.py", "collectstatic", "--noinput"])

    def handle(self, *args, **options):
        build_dir = "./frontend_build"
        target_dir = "./compiled"
        for dirpath in (build_dir, target_dir):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
        os.environ["TMPDIR"] = build_dir
        self.run_collectstatic()
        regulations_directory = self.find_regulations_directory()
        frontend_files = (
            "package.json",
            "bower.json",
            "Gruntfile.js",
            ".eslintrc"
        )
        for f_file in frontend_files:
            source = "%s/%s" %(regulations_directory, f_file)
            shutil.copy(source, "%s/" % build_dir)
        with codecs.open("%s/config.json" % build_dir, "w",
                         encoding="utf-8") as f:
            f.write('{"frontEndPath": "static/regulations"}')
        os.chdir(build_dir)
        subprocess.call(["npm", "install", "grunt-cli", "bower"])
        subprocess.call(["npm", "install"])
        os.chdir("..")
        shutil.copytree("%s/static/regulations" % build_dir, target_dir)

import codecs
import distutils
import regulations
import os
import shutil
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Build the frontend, including local overrides.'

    def find_regulations_directory(self):
        child = regulations.__file__
        child_dir = os.path.split(child)[0]
        return os.path.split(child_dir)[0]

    def run_collectstatic(self):
        return_code = subprocess.call(["python", "manage.py", "collectstatic",
                                       "--noinput"])

    def handle(self, *args, **options):
        build_dir = "./frontend_build"
        target_dir = "./compiled"
        for dirpath in (build_dir, target_dir):
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
        os.environ["TMPDIR"] = build_dir
        self.run_collectstatic()
        regulations_directory = self.find_regulations_directory()
        for f in (
            "package.json",
            "bower.json",
            "Gruntfile.js",
            ".eslintrc"
        ):
            shutil.copy("%s/%s" %(regulations_directory, f),
                        "%s/" % build_dir)
        with codecs.open("%s/config.json" % build_dir, "w", encoding="utf-8") as f:
            f.write('{"frontEndPath": "static/regulations"}')
        os.chdir(build_dir)
        return_code = subprocess.call(["npm", "install", "grunt-cli", "bower"])
        return_code = subprocess.call(["npm", "install"])
        os.chdir("..")
        shutil.copytree("%s/static/regulations" % build_dir, target_dir)

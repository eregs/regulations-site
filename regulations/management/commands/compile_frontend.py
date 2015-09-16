import codecs
import distutils
from os import environ, mkdir, path
import regulations
import shutil
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Build the frontend, including overrides.'

    def find_regulations_directory(self):
        child = regulations.__file__
        child_dir = path.split(child)[0]
        return path.split(child_dir)[0]

    def run_collectstatic(self):
        call_command("collectstatic", noinput=True)

    def write_file(self, filename, markup):
        """ Write out a file using the UTF-8 codec. """
        f = codecs.open(filename, 'w', encoding='utf-8')
        f.write(markup)
        f.close()

    def get_regulation_version(self, **options):
        """ Get the regulation part and regulation version from the command line arguments. """
        regulation_part = options.get('regulation_part')
        regulation_version = options.get('regulation_version')

        if not regulation_part or not regulation_version:
            usage_string = "Usage: python manage.py generate_regulation  %s\n"  % Command.args
            raise CommandError(usage_string)
        return (regulation_part, regulation_version)

    def handle(self, *args, **options):
        import rlcompleter; import pdb; zcomp = locals(); zcomp.update(globals()); pdb.Pdb.complete = rlcompleter.Completer(zcomp).complete; pdb.set_trace()
        """
        target = "./frontend_build"
        # put in some checks before this?
        shutil.rmtree("./compiled")
        environ["TMDDIR"] = target
        self.run_collectstatic()
        regulations_directory = self.find_regulations_directory()
        for f in (
            "package.json",
            "bower.json",
            "Gruntfile.js",
            ".eslintrc"
        ):
            shutil.copy("%s/%s" %(regulations_directory, f), target)
        with codecs.open("%s/config.json" % target, "w", encoding="utf-8") as f:
            f.write('{"frontEndPath": "static/regulations"}')
        os.chdir(target)
        return_code = subprocess.call(["npm", "install", "grunt-cli", "bower"])
        return_code = subprocess.call(["npm", "install"])
        shutil.copytree("./static/regulations", "../compiled")
        os.chdir("..")
        """

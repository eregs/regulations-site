import os
from subprocess import call     # nosec  - see usage below

from distutils.command.build_ext import build_ext as _build_ext
from setuptools import Command, find_packages, setup
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg


class build_frontend(Command):
    """ A command class to run `frontendbuild.sh` """
    description = 'build front-end JavaScript and CSS'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Safe because: calling our own script
        call(['./frontendbuild.sh'],    # nosec
             cwd=os.path.dirname(os.path.abspath(__file__)))


class build_ext(_build_ext):
    """ A build_ext subclass that adds build_frontend """
    def run(self):
        self.run_command('build_frontend')
        _build_ext.run(self)


class bdist_egg(_bdist_egg):
    """ A bdist_egg subclass that runs build_frontend """
    def run(self):
        self.run_command('build_frontend')
        _bdist_egg.run(self)


setup(
    name="regulations",
    version="5.0.0",
    packages=find_packages(),
    install_requires=[
        'boto3',
        'cached-property',
        'celery',
        'django>=1.8,<1.10',
        'enum34',
        'requests',
        'six',
        'requests-toolbelt',
    ],
    cmdclass={
        'build_frontend': build_frontend,
        'build_ext': build_ext,
        'bdist_egg': bdist_egg,
    },
    classifiers=[
        'License :: Public Domain',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication'
    ]
)

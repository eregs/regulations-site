from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

OFFLINE_OUTPUT_DIR = '/tmp/'

INSTALLED_APPS += (
    'django_nose',
)

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=regulations',
    '--exclude-dir=regulations/uitests'
]

try:
    from local_settings import *
except ImportError:
    pass

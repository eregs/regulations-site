from .base import *

DEBUG = True

CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
CACHES['eregs_longterm_cache']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
CACHES['api_cache']['TIMEOUT'] = 5  # roughly per request

ROOT_URLCONF = 'regulations.all_urls'
INSTALLED_APPS = INSTALLED_APPS + ('notice_comment',)

try:
    from local_settings import *
except ImportError:
    pass

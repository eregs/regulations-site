import os
from os.path import join, abspath, dirname
import tempfile

from distutils.spawn import find_executable
from django.utils.crypto import get_random_string


here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..", "..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'regsite.db'
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
if 'TMPDIR' in os.environ:
    STATIC_ROOT = os.environ['TMPDIR'] + '/static/'
else:
    STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_string(50))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "context_processors": (
                # "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request",
                "regulations.context.eregs_globals",
            ),
            # List of callables that know how to import templates from various
            # sources.
            "loaders": [
                ('django.template.loaders.cached.Loader', (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader'))
            ],
        }
    },
]


# Order from
# https://docs.djangoproject.com/en/1.9/ref/middleware/#middleware-ordering
MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

ROOT_URLCONF = 'regulations.urls'

INSTALLED_APPS = (
    # Note: no admin
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'regulations.apps.RegulationsConfig',
)

# eregs specific settings

# The base URL for the API that we use to access layers and the regulation.
API_BASE = os.environ.get('EREGS_API_BASE', '')

DATE_FORMAT = 'n/j/Y'

# Analytics settings

ANALYTICS = {
    'GOOGLE': {
       'GTM_SITE_ID': '',
       'GA_SITE_ID': '',
    },
    'DAP': {
        'AGENCY': '',
        'SUBAGENCY': '',
    },
}

#   Use the 'source' directory; useful for development
JS_DEBUG = False

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': tempfile.mkdtemp('eregs_cache'),
    },
    'eregs_longterm_cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': tempfile.mkdtemp('eregs_longterm_cache'),
        'TIMEOUT': 60*60*24*15,     # 15 days
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        },
    },
    'api_cache': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api_cache_memory',
        'TIMEOUT': 3600,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    },
    'regs_gov_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_KEY_PREFIX = 'eregs'
CACHE_MIDDLEWARE_SECONDS = 600
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# Where should we look for data?
DATA_LAYERS = (
    'regulations.generator.layers.defined.DefinedLayer',
    'regulations.generator.layers.definitions.DefinitionsLayer',
    'regulations.generator.layers.external_citation.ExternalCitationLayer',
    'regulations.generator.layers.footnotes.FootnotesLayer',
    'regulations.generator.layers.formatting.FormattingLayer',
    'regulations.generator.layers.internal_citation.InternalCitationLayer',
    # Should likely be moved to a CFPB-specific module
    'regulations.generator.layers.interpretations.InterpretationsLayer',
    'regulations.generator.layers.key_terms.KeyTermsLayer',
    'regulations.generator.layers.meta.MetaLayer',
    'regulations.generator.layers.paragraph_markers.MarkerHidingLayer',
    'regulations.generator.layers.paragraph_markers.MarkerInfoLayer',
    'regulations.generator.layers.toc_applier.TableOfContentsLayer',
    'regulations.generator.layers.graphics.GraphicsLayer',
)

SIDEBARS = (
    'regulations.generator.sidebar.analyses.Analyses',
    'regulations.generator.sidebar.help.Help',
)

ATTACHMENT_BUCKET = os.getenv('S3_BUCKET')
ATTACHMENT_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
ATTACHMENT_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')

# regulations.gov restrictions
ATTACHMENT_MAX_SIZE = 1024 * 1024 * 10
ATTACHMENT_PREVIEW_PREFIX = 'preview'
VALID_ATTACHMENT_EXTENSIONS = set([
    "bmp", "doc", "xls", "pdf", "gif", "htm", "html", "jpg", "jpeg",
    "png", "ppt", "rtf", "sgml", "tiff", "tif", "txt", "wpd", "xml",
    "docx", "xlsx", "pptx"])
MAX_ATTACHMENT_COUNT = 10

REGS_GOV_API_URL = os.environ.get('REGS_GOV_API_URL')
REGS_GOV_API_KEY = os.environ.get('REGS_GOV_API_KEY')

COMMENT_DOCUMENT_ID = os.getenv('DOCUMENT_ID')
WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH',
                             find_executable('wkhtmltopdf'))

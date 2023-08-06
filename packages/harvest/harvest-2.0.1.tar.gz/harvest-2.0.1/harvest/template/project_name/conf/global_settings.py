import os

# Import global settings to make it easier to extend settings.
from django.conf.global_settings import *

# Import the project module to calculate directories relative to the module
# location.
PROJECT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')

# List all Django apps here. Note that standard Python libraries should not
# be added to this list since Django will not recognize them as apps anyway.
# An app is really only an "app" if a `models` module or package is defined.
# Read more about projects vs. apps here:
# https://docs.djangoproject.com/en/1.3/intro/tutorial01/#creating-models
INSTALLED_APPS = (
    '{{ project_name }}',

    'south',
    'serrano',
    'avocado',
    'modeltree',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
)


#
# ADMINISTRATIVE
#

# Admins receive any error messages by email if DEBUG is False
ADMINS = ()

# Managers receive broken link emails if SEND_BROKEN_LINK_EMAILS is True
MANAGERS = ADMINS

# List of IP addresses which will show debug comments
INTERNAL_IPS = ('127.0.0.1', '::1')

DEBUG = True
TEMPLATE_DEBUG = DEBUG


#
# DATABASES
# Each database can be specified here, but passwords should be in a separate
# file that is not versioned. Use ``local_settings.py``.
#

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, '{{ project_name }}.db')
    }
}


#
# LOCALITY
#

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = False


#
# STATIC AND MEDIA
# The application's static files should be placed in the STATIC_ROOT in
# addition to other static files found in third-party apps. The MEDIA_ROOT
# is intended for user uploaded files.
#

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, '_site/media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, '_site/static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
# Put strings here, like "/home/html/static" or "C:/www/django/static".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
STATICFILES_DIRS = ()

#
# TEMPLATES
#

# Project level templates and template directories that override
# third-party app templates.
TEMPLATE_DIRS = ()

# Context processors are simply functions that return a dict which augments the
# template context.
TEMPLATE_CONTEXT_PROCESSORS += (
    'django.core.context_processors.request',
    '{{ project_name }}.context_processors.static',
)


#
# URLS
#

# FORCE_SCRIPT_NAME overrides the interpreted 'SCRIPT_NAME' provided by the
# web server. since the URLs below are used for various purposes outside of
# the WSGI application (static and media files), these need to be updated to
# reflect this discrepancy.
FORCE_SCRIPT_NAME = ''

ROOT_URLCONF = '{{ project_name }}.conf.urls'

# LOGIN_URL = '/login/'
# LOGOUT_URL = '/logout/'

# For non-publicly accessible applications, the siteauth app can be used to
# restrict access site-wide.
# SITEAUTH_ACCESS_ORDER = 'allow/deny'
#
# SITEAUTH_ALLOW_URLS = (
#     r'^$',
#     r'^log(in|out)/',
#     r'^password/reset/',
#     r'^(register|verify)/',
# )

#
# MIDDLEWARE
#

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'serrano.middleware.SessionMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
)


#
# EMAIL
#

SUPPORT_EMAIL = 'support@example.com'
DEFAULT_FROM_EMAIL = 'support@example.com'
EMAIL_SUBJECT_PREFIX = '[{{ project_name }}] '
SEND_BROKEN_LINK_EMAILS = False


#
# LOGGING
#

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
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


#
# CACHE
#

# For production environments, the memcached backend is highly recommended
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique',
        'KEY_PREFIX': '{{ project_name}}',
        'VERSION': 1,
    }
}

CACHE_MIDDLEWARE_SECONDS = 0

# This is not necessary to set if the above `KEY_PREFIX` value is set since
# the `KEY_PREFIX` namespaces all cache set by this application
CACHE_MIDDLEWARE_KEY_PREFIX = '{{ project_name }}'


#
# SESSIONS AND COOKIES
#

CSRF_COOKIE_NAME = '{{ project_name }}_csrftoken'

# SESSION_COOKIE_AGE = 60 * 20
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_COOKIE_NAME = '{{ project_name }}_sessionid'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False


#
# OTHER PROJECT SETTINGS
#

# USE_ETAGS = True
IGNORABLE_404_PATHS = (
    r'robots.txt$',
    r'favicon.ico$',
)

#
# VARIOUS APP SETTINGS
#

# The primary key of the ``Site`` object for the Sites Framework
SITE_ID = 1


#
# ModelTrees Configuration
#

# MODELTREES = {
#     'default': {
#         'model': '',
#     }
# }

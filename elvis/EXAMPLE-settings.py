"""

*** THIS FILE SHOULD BE MODIFIED with your local settings, then saved as base.py ***


Django settings for elvis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# for scheduling file removal using celery
from celery import schedules

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.abspath('./')

# Automatically adjust settings to be suitable or insuitable for proudction environments
# CRA: I used this to help...
#      https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False


# Simple Settings
# ===============

ALLOWED_HOSTS = ['database.elvisproject.ca', 'db-devel.elvisproject.ca']

#TODO Write email settings for password recover feature after depoloyment.

with open('/etc/elvis_secretkey.txt') as f:
    SECRET_KEY = f.read().strip()


# Application Definition
# ======================
ROOT_URLCONF = 'elvis.urls'
WSGI_APPLICATION = 'elvis.wsgi.application'
SITE_ID = 1

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
    'elvis',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.template.context_processors.debug",
    "django.template.context_processors.i18n",
    "django.template.context_processors.media",
    "django.template.context_processors.static",
    "django.template.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# This is only a dummy cache so the site won't break. You should enable one
# of the others.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
# Decide which kind of cache you would like to use:
#
# This is way faster, but requires you install redis and django-redis.
#
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': "redis://127.0.0.1:6379",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#         'TIMEOUT': None
#
#     }
# }
#
# The DB cache is slower, but only requires that you execute
# manage.py createcachetable in order to begin using it.
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'my_cache_table',
#     }
# }

# Database Configuration
# ======================
BROKER_URL = 'django://'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'elvis2',
        'USER': 'elvisdatabase',
        'PASSWORD': '5115C67O2v3GN31T49Md'
        }
}

# Email Settings
# ==============
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'elvisdatabase@gmail.com'
with open('/etc/elvis_emailpass.txt') as f:
    EMAIL_HOST_PASSWORD = f.read().strip()

# Captcha Settings
# ================
RECAPTCHA_PUBLIC_KEY = "6LfV4gsTAAAAAGK8vA-O2RrABlIb_XbNywrxJrTS"

with open('/etc/elvis_captchakey.txt') as f:
    RECAPTCHA_PRIVATE_KEY = f.read().strip()

# Internationalization
# ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Media and Static Files
# ======================
# CRA: we used to have composer images and user profile images; if we need
#      them back, check commit dc8f8afe75b7137440c6488483566b8e2c366379
MEDIA_URL = '/media/'
MEDIA_ROOT = '/srv/webapps/elvis-database/media_root/'


STATIC_URL = '/static/'
STATIC_ROOT = '/srv/webapps/elvis-database/static_root/'


# Solr Settings
# =============

SOLR_SERVER = "http://localhost:8080/elvis-solr"

SEARCH_FILTERS_DICT = {
    'fcp': 'elvis_composer',
    'fp': 'elvis_piece',
    'fm': 'elvis_movement',
    'ft': 'elvis_tag',
    'fu': 'elvis_user',
    }
FACET_NAMES = {
    'type': "Result Type",
    'composer_name': "Composer",
    "number_of_voices": "Number of Voices",
    "tags": "Tags",
    "parent_collection_names": "Collection",
    }
TYPE_NAMES={
    'elvis_user': "Users",
    'elvis_tag': "Tags",
    'elvis_movement': "Movements",
    'elvis_piece': "Pieces",
    'elvis_composer': "Composers",
    'elvis_collection': "Collections",
    }

# Celery Settings
# ===============
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
# See documentation for crontab settings
CELERYBEAT_SCHEDULE = {
    'clean_zip_files': {
        'task': 'elvis.celery.clean_zip_files',
        'schedule': schedules.crontab(minute=0, hour=0)
    },
    }

# Elvis Web App Settings
# ======================
ELVIS_EXTENSIONS = ['.xml', '.mxl', '.krn', '.md', '.nwc', '.tntxt', '.capx', '.abc', '.mid', '.midi', '.pdf', '.mei']
ELVIS_BAD_PREFIX = ['.', '..', '_', '__']
SUGGEST_DICTS = ['composerSuggest', 'pieceSuggest', 'collectionSuggest', 'languageSuggest', 'genreSuggest', 'locationSuggest', 'sourceSuggest', 'instrumentSuggest', 'tagSuggest']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/srv/webapps/elvis-database/debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
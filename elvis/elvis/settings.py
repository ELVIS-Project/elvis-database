"""
Django settings for elvis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
from __future__ import absolute_import

# for dynamic SECRET_KEY generation
from random import SystemRandom

# for scheduling file removal using celery
from celery import schedules

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(__file__)

# Automatically adjust settings to be suitable or insuitable for proudction environments
# CRA: I used this to help...
#      https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
# SECURITY WARNING: don't run with debug turned on in production!
# CRA: Set "LILLIO" to True if you're Lillio.
PRODUCTION = False
LILLIO = False if PRODUCTION else True  # we'll be Lillio by default...


# Simple Settings
# ===============
DEBUG = False if PRODUCTION else True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['database.elvisproject.ca', 'db-devel.elvisproject.ca'] if PRODUCTION else []

if PRODUCTION:
    # TODO: Try loading from a temp file; if not present, automatically generate SECRET_KEY then
    #       save it to the temp file. This would mean changing the SECRET_KEY on every reboot,
    #       which isn't particularly detrimental to anyone.
    SECRET_KEY = ''
else:
    SECRET_KEY = '85k%wv*)+qz$(iwcd(!v9=nn@&gb5+_%if)(fxbgzz&4g2+l%t'


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
    'elvis',
    'rest_framework',
    'rest_framework.authtoken',
    'django_extensions',
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


# Database Configuration
# ======================
if not PRODUCTION and LILLIO:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'elvis',
            'USER': '',
            'PASSWORD': '',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'elvisdatabase',
            'USER': 'elvisdatabase',
            'PASSWORD': 'asdf1234',
            'HOST': '',  # empty means localhost through domain sockets
            'PORT': '',  # empty means 5432
        }
    }


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

if DEBUG and LILLIO:
    MEDIA_ROOT = "/Users/lmok/Documents/workspace/elvis-site/elvis"
#elif DEBUG:
#    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', '..', 'media_root')
# httpd will serve static files from this directory
STATIC_URL = '/static/'
if DEBUG and LILLIO:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/Users/lmok/Documents/workspace/elvis-site/elvis/elvis/static/'
elif DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, '..', '..', 'static_root')
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Solr Settings
# =============
if LILLIO:
    SOLR_SERVER = "http://localhost:8080/elvis-solr"
else:
    SOLR_SERVER = "http://localhost:8080/elvis-solr"
SEARCH_FILTERS_DICT = {
    'fcp': 'elvis_composer',
    'fp': 'elvis_piece',
    'fm': 'elvis_movement',
    'fcr': 'elvis_corpus',
    'ft': 'elvis_tag',
    'fu': 'elvis_user',
}
FACET_NAMES = {
    'type': "Result Type",
    'composer_name': "Composer",
    'parent_corpus_name': "Corpus",
    "number_of_voices": "Number of Voices",
    "tags": "Tags",
    "parent_collection_names": "Collection",
}
TYPE_NAMES={
    'elvis_user': "Users",
    'elvis_tag': "Tags",
    'elvis_corpus': "Corpora",
    'elvis_movement': "Movements",
    'elvis_piece': "Pieces",
    'elvis_composer': "Composers",
    'elvis_collection': "Collections",
}

# Celery Settings
# ===============
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
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
ELVIS_EXTENSIONS = ['.xml', '.mxl', '.krn', '.md', '.nwc', '.tntxt', '.capx', '.abc', '.mid', '.midi']


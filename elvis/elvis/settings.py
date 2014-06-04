"""
Django settings for elvis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# for dynamic SECRET_KEY generation
from random import SystemRandom

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

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
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'elvis',
        'USER': 'elvis-database',
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
elif DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, '..', '..', '..', 'media_root')
# httpd will serve static files from this directory
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'


# Solr Settings
# =============
SOLR_SERVER = "http://localhost:8080/elvis-solr"
SEARCH_FILTERS_DICT = {
    'fcp': 'elvis_composer',
    'fp': 'elvis_piece',
    'fm': 'elvis_movement',
    'fcr': 'elvis_corpus',
    'ft': 'elvis_tag',
    'fu': 'elvis_user',
}


# Celery Settings
# ===============
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

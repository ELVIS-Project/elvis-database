

import os

from celery import Celery
from django.conf import settings

# Celery can be started by running `celery -A elvis worker -l info` from the elvis-database/elvis dir while sourced
# from the virtualenv used to run the django project.

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elvis.settings.base')

app = Celery('elvis', broker=settings.BROKER_URL, backend=settings.CELERY_RESULT_BACKEND, include=['elvis.tasks'])

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(('Request: {0!r}'.format(self.request)))
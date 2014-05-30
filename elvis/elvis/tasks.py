from __future__ import absolute_import

from elvis.celery import app

from django.conf import settings

# For tracking progress
from time import sleep
from celery.result import AsyncResult
from celery import task, current_task

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json
from django.conf.urls import patterns, url



# LM: 
# Check this out: http://massivescale.blogspot.ca/2011/09/celery-task-queue-with-php.html
# TODO: Change unicode encoding to utf for terminal commands
@app.task(name='elvis.celery.zip_files')
def zip_files(paths, username):
    import uuid, subprocess, string, os, shutil, datetime, zipfile

    # Create unique dummy folder in user_downloads using uuid
    dummy_folder = str(uuid.uuid4())
    dummy_root_dir = os.path.join(settings.MEDIA_ROOT, 'user_downloads', username)
    dummy_path = os.path.join(dummy_root_dir, dummy_folder)
    #print(dummy_path)

    if not os.path.exists(dummy_path):
            os.makedirs(dummy_path)

    # cp the requested files into dummy_folder
    zip_name = username+"-"+datetime.datetime.utcnow().date().isoformat()

    # Iterative Zip
    os.chdir(dummy_path)
    archive_file = zipfile.ZipFile(zip_name, 'a')

    total = len(paths)
    i = 0
    for item in paths:
        # tokenise to remove the actual file name from path name
        file_name = os.path.basename(item)
        shutil.copy2(item, os.path.join(dummy_path, file_name))
        archive_file.write(file_name)
        sleep(5)
        i += 1
        zip_files.update_state(state='PROGRESS', meta={'curr': i, 'total': total})

    # Now create the zip
    
    # Have to cd to directory for archive output... don't know why make_archive has a root_dir argument that doesn't do this
    #os.chdir(dummy_root_dir)
    #zip_path = shutil.make_archive(zip_name, "zip", dummy_root_dir, dummy_path)
    #print(zip_name)

    # Iterative Zip

    archive_file.close()

    zip_path = os.path.join(dummy_path, zip_name)

    #print(dummy_root_dir, dummy_path)
    return zip_path

@app.task()
def zip_status_check(zip_task_id):
    """ Get some rest, asynchronously, and update the state all the time """
    for i in range(100):
        sleep(0.1)
        zip_files.update_state(task_id = zip_task_id, state='PROGRESS',
            meta={'curr': i, 'total': 100})

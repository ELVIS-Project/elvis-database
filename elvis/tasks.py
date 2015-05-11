from __future__ import absolute_import

from elvis.celery import app

from django.conf import settings

# For tracking progress
import time
from celery.result import AsyncResult
from celery import task, current_task

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import json
from django.conf.urls import patterns, url
import os
import shutil

def int_round(num):
    if (num > 0):
        return int(num+.5)
    else:
        return int(num-.5)

# LM: 
# Check this out: http://massivescale.blogspot.ca/2011/09/celery-task-queue-with-php.html
# TODO: Cleanup
@app.task(name='elvis.celery.zip_files')
def zip_files(paths, username):
    # Start with status at 0 - so jQuery has something to do
    i = 0
    total = len(paths)
    percent = int_round(float(i) / float(total))  * 100
    zip_files.update_state(state='PROGRESS', meta={'curr': i, 'total': total, 'percent': percent })

    # Now do imports after that (again so jQuery has something to do)
    import uuid, subprocess, string, os, shutil, datetime, zipfile

    # Create unique dummy folder in user_downloads using uuid
    dummy_folder = str(uuid.uuid4())
    # User's download folder
    dummy_root_dir = os.path.join(settings.MEDIA_ROOT, 'user_downloads', username)
    # The path to this particular unique folder with the files
    dummy_path = os.path.join(dummy_root_dir, dummy_folder)

    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    # create name of zipped file
    zip_name = "{0}-{1}.zip".format(username, datetime.datetime.utcnow().date().isoformat())

    # Create zip archive iteratively by copying first, then adding to archive file
    # Change dir to the path
    os.chdir(dummy_path)
    # Zip the file to that directory
    archive_file = zipfile.ZipFile(zip_name, 'a')
    
    for item in paths:
        # tokenise to remove the actual file name from path name
        file_name = os.path.basename(item)
        shutil.copy2(item, os.path.join(dummy_path, file_name))
        archive_file.write(file_name)
        i += 1
        percent = int(float(i) * 100.0 / float(total))
        zip_files.update_state(state='PROGRESS', meta={'curr': i, 'total': total, 'percent': percent})

    archive_file.close()
    zip_files.update_state(state='PROGRESS', meta={'curr': total, 'total': total, 'percent': 100})
    # Path to the archive file
    zip_path = os.path.join(dummy_path, zip_name)

    return {"path": zip_path, "percent" : 100}

@app.task(name='elvis.celery.clean_zip_files')
def clean_zip_files():
    print "clean_zip_files beating."
    downloads_dir_path = os.path.join(settings.MEDIA_ROOT, 'user_downloads')
    if not os.path.isdir(downloads_dir_path):
        print 'User_downloads not detected'
        return False
    # Get the time a day before now
    one_day_ago = time.time() - 86400
    # Look at all the temporary download task folders
    for user_dir in os.listdir(downloads_dir_path):
        user_dir_path = os.path.join(downloads_dir_path, user_dir)
        for task_dir in os.listdir(user_dir_path):
            # Join path accordingly, check the time
            task_dir_path = os.path.join(user_dir_path, task_dir)
            modified_time = os.path.getmtime(task_dir_path)
            if modified_time < one_day_ago and os.path.isdir(task_dir_path):
                # Uncomment when sure of correct file detection
                print "Deleting " + str(task_dir_path)
                shutil.rmtree(task_dir_path)
    return True



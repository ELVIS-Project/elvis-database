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
    percent = int_round((i * 100) / total)
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
        sleep(1)
        i += 1
        percent = int_round((i * 100) / total)
        zip_files.update_state(state='PROGRESS', meta={'curr': i, 'total': total, 'percent': percent})


    archive_file.close()
    zip_files.update_state(state='PROGRESS', meta={'curr': total, 'total': total, 'percent': 100})
    # Path to the archive file
    zip_path = os.path.join(dummy_path, zip_name)

    #print(dummy_root_dir, dummy_path)
    return {"path": zip_path, "percent" : 110}



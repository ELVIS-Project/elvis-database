
import urllib.request, urllib.parse, urllib.error
import os
import time
import shutil
import uuid
import datetime
import zipfile

from django.conf import settings
from .celery import app

@app.task(name='elvis.elvis.rebuild_suggesters')
def rebuild_suggester_dicts():
    """Rebuild all suggester dictionaries in Solr"""
    for d in settings.SUGGEST_DICTS:
        url = settings.SOLR_SERVER + "/suggest/?suggest.dictionary={0}&suggest.reload=true".format(d)
        urllib.request.urlopen(url)

@app.task(name='elvis.elvis.zip_files')
def zip_files(paths, username):
    # Start with status at 0 - so jQuery has something to do
    i = 0
    total = len(paths)
    percent = round((i/float(total)) * 100)
    zip_files.update_state(state='PROGRESS', meta={'curr': i, 'total': total, 'percent': percent})

    # Create unique dummy folder in user_downloads using uuid
    dummy_folder = str(uuid.uuid4())
    # User's download folder
    dummy_root_dir = os.path.join(settings.MEDIA_ROOT, 'user_downloads', username)
    # The path to this particular unique folder with the files
    dummy_path = os.path.join(dummy_root_dir, dummy_folder)

    if not os.path.exists(dummy_path):
        os.makedirs(dummy_path)

    # create name of zipped file
    zip_name = "{0}-{1}-ElvisDB.zip".format(datetime.datetime.utcnow().strftime("%y-%m-%d-T(%H-%M-%S)-"), username)

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
    zip_path = os.path.join(dummy_path.replace(settings.MEDIA_ROOT, ""), zip_name)
    delete_zip_file.apply_async(args=[dummy_path], countdown=600)

    return {"path": zip_path, "percent" : 100}

@app.task(name='elvis.elvis.delete_zip_file')
def delete_zip_file(path):
    shutil.rmtree(path)

def int_round(num):
    if (num > 0):
        return int(num+.5)
    else:
        return int(num-.5)
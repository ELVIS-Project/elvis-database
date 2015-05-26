from django.http import HttpResponse
from django.conf import settings
from django.core.files.base import File

from elvis.exceptions import NoFilesError
from elvis.models import Attachment
from elvis.models import Composer

import json
import urllib
import urllib2
import os
import zipfile
import datetime
import pdb


def solr_suggest(request):
    results = []

    if request.method == "GET" and request.GET.has_key(u'q') and request.GET.has_key(u'd'):
        value = request.GET['q']
        dictionary = request.GET['d']
        if len(value) > 1:
            json_string = urllib2.urlopen(
                settings.SOLR_SERVER + "/suggest/?wt=json&suggest.dictionary={0}&q={1}".format(dictionary, value))
            resp = json.loads(json_string.read())['suggest']['{0}'.format(dictionary)]
            data = resp[resp.keys()[0]]
            if data['numFound'] > 0:
                for suggestion in data['suggestions']:
                    results.append({'name': suggestion['term']})
    j_results = json.dumps(results)
    return HttpResponse(j_results, content_type="json")

# Uploads files to the media/temp directory. Automatically unzips
# any zip archives. Returns a list of uploaded files.
def upload_files(request):
    files = []

    if not os.path.exists(settings.MEDIA_ROOT + 'temp/'):
        os.makedirs(settings.MEDIA_ROOT + 'temp/')

    file_list = request.FILES.getlist('files')

    for f in file_list:
        # If the file has an accepted extension, upload it.
        if any(f.name.endswith(x) for x in settings.ELVIS_EXTENSIONS) and not any(f.name.startswith(x) for x in settings.ELVIS_BAD_PREFIX):
            with open(settings.MEDIA_ROOT + 'temp/' + f.name, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
                files.append({'name': f.name,
                              'uploader': request.user.username,
                              'path': settings.MEDIA_ROOT + 'temp/'})

        # Or, if the file is a zip file, upload, extract good files, then delete the archive.
        if f.name.endswith('.zip'):
            with open(settings.MEDIA_ROOT + 'temp/' + f.name, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            try:
                unzipped_files = unzip_file(settings.MEDIA_ROOT + 'temp/', f.name)
                for file_name in unzipped_files:
                    files.append({'name': file_name,
                                  'uploader': request.user.username,
                                  'path': settings.MEDIA_ROOT + 'temp/'})
            except zipfile.BadZipfile:
                files.append({'name': f.name, 'error': "Zip file could not be opened."})

            os.remove(settings.MEDIA_ROOT + 'temp/' + f.name)

    return files


# Unzips a zip file, extracting only files with the extensions in settings.ELVIS_EXTENSIONS.
# The files are placed in the same directory as the archive. Returns a list of extracted filenames.
def unzip_file(file_dir, file_name):
    files = []
    zipped_file = zipfile.ZipFile(file_dir + file_name, 'r')
    file_contents = zipped_file.namelist()

    for f_name in file_contents:
        if (any(f_name.endswith(x) for x in settings.ELVIS_EXTENSIONS) and
                not any(f_name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and
                not any(x in f_name for x in ('/', '\\'))):
            zipped_file.extract(f_name, file_dir)
            files.append(f_name)

    zipped_file.close()
    return files

# Takes the request.FILES and uploads them, processes them, then creates attachments and adds them to parents
# attachment field.
def handle_attachments(request, parent):
    results = []

    files = upload_files(request)
    # TODO redirect to an error page or throw up a message if nothing is acceptable.
    if files == []:
        pass

    for f in files:
        att = Attachment(description="TESTING")
        att.save()  # needed to create hash dir.
        att.uploader = request.user

        new_name = "{0}_{1}.".format(parent.title.replace(" ", "-"), parent.composer.name.replace(" ", "-")) + f['name'].rsplit('.')[-1]
        os.rename(f['path'] + f['name'], f['path'] + new_name)

        with open("{0}/{1}".format(f['path'], new_name), 'r+') as dest:
            file_content = File(dest)
            att.attachment.save("{0}/{1}".format(att.attachment_path, new_name), file_content)
        os.remove(f['path'] + new_name)
        att.save()
        results.append(att)

    for att in results:
        parent.attachments.add(att)

    parent.save()


#TODO implement better behaviour for creating composers.
def handle_composer(composer):
    try:
        new_composer = Composer.objects.get(name=composer)
        return new_composer
    except:
        new_composer = Composer(name=composer, created=datetime.datetime.now())
        new_composer.save()
        return new_composer
    pass

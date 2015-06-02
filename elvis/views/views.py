from django.http import HttpResponse
from django.conf import settings
from django.core.files.base import File
from elvis.models import Attachment
from elvis.models import Movement
from elvis.models import Composer
from elvis.models import Collection
from elvis.models import Language
from elvis.models import Location
from elvis.models import Source
from elvis.models import InstrumentVoice
from django.db.models import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

import json
import urllib2
import os
import zipfile
import datetime
import pdb


def solr_suggest(request):
    results = []

    if request.method == "GET" and 'q' in request.GET and 'd' in request.GET:
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


# Uploads files to the media/temp directory. Automatically unzips any zip archives. Returns a list of uploaded files.
def upload_files(request, **kwargs):
    files = []

    if not os.path.exists(settings.MEDIA_ROOT + 'temp/'):
        os.makedirs(settings.MEDIA_ROOT + 'temp/')

    if 'file_name' in kwargs:
        file_list = request.FILES.getlist(kwargs['file_name'])
    else:
        file_list = request.FILES.getlist('piece_att_files')

    for f in file_list:
        # If the file has an accepted extension, upload it.
        if not any(f.name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and any(
                f.name.endswith(x) for x in settings.ELVIS_EXTENSIONS):
            upload_file(f, settings.MEDIA_ROOT + 'temp/' + f.name)
            files.append({'name': f.name,
                          'uploader': request.user.username,
                          'path': settings.MEDIA_ROOT + 'temp/'})

        # Or, if the file is a zip file, upload, extract good files, then delete the archive.
        if f.name.endswith('.zip'):
            upload_file(f, settings.MEDIA_ROOT + 'temp/' + f.name)

            try:
                unzipped_files = unzip_file(settings.MEDIA_ROOT + 'temp/', f.name, delete_after=True)
                for file_name in unzipped_files:
                    files.append({'name': file_name,
                                  'uploader': request.user.username,
                                  'path': settings.MEDIA_ROOT + 'temp/'})
            except zipfile.BadZipfile:
                files.append({'name': f.name, 'error': "Zip file could not be opened."})

    return files


# Uploads the in-memory file to the given path.
def upload_file(mem_file, local_path):
    with open(local_path, 'wb+') as destination:
        for chunk in mem_file.chunks():
            destination.write(chunk)


# Unzips a zip file, extracting only files with the extensions in settings.ELVIS_EXTENSIONS.
# The files are placed in the same directory as the archive. Returns a list of extracted filenames.
def unzip_file(file_dir, file_name, **kwargs):
    files = []
    zipped_file = zipfile.ZipFile(file_dir + file_name, 'r')
    file_contents = zipped_file.namelist()

    for f_name in file_contents:
        if (not any(f_name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and
                any(f_name.endswith(x) for x in settings.ELVIS_EXTENSIONS) and
                not any(x in f_name for x in ('/', '\\'))):
            zipped_file.extract(f_name, file_dir)
            files.append(f_name)

    zipped_file.close()

    if 'delete_after' in kwargs and kwargs['delete_after']:
        os.remove(file_dir + file_name)

    return files


# Takes the request.FILES and uploads them, processes them, then creates attachments and adds them to parents
# attachment field.
def handle_attachments(request, parent, **kwargs):
    results = []

    if 'file_name' in kwargs:
        files = upload_files(request, file_name=kwargs['file_name'])
    else:
        files = upload_files(request, file_name='piece_att_files')

    for f in files:
        att = Attachment(description="TESTING")
        att.save()  # needed to create hash dir.
        att.uploader = request.user

        new_name = "{0}_{1}.{2}".format(parent.title.replace(" ", "-"),
                                        parent.composer.name.replace(" ", "-"),
                                        f['name'].rsplit('.')[-1])
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

    return results


# Creates the movements in the request and attaches them to their parent.
# Returns a list of movements and attachments that have been created.
def handle_movements(request, parent):
    results = []
    attachments = []
    movements = {}
    for item in request.POST:
        if item.startswith("mv_title") and request.POST[item]:
            mv_name = request.POST[item]
            mv_num = item[9:]
            movements[mv_num] = (mv_name, mv_num)

    keys = movements.keys()
    keys.sort()
    i = 1

    for k in keys:
        new_mv = Movement(title=movements[k][0],
                          position=i,
                          date_of_composition=parent.date_of_composition,
                          date_of_composition2=parent.date_of_composition2,
                          composer=parent.composer,
                          piece=parent,
                          comment="TESTING")
        new_mv.save()
        attachments.extend(handle_attachments(request, new_mv, file_name="mv_files_" + movements[k][1], parent_type='movement'))
        new_mv.save()
        results.append(new_mv)
        i += 1

    results.extend(attachments)
    return results


# Queries the database for the model. If the model does not exist, the method creates
# a new one with the given name. Also works for semicolon seperated lists. If given a Cleanup object, it will append
# all newly created models to the objects list so they can be deleted if there is a problem later in the process.
# Returns a list of the models which were found/created.
def abstract_model_handler(model_name, model_type, cleanup, **kwargs):

    if model_type == "Composer":
        composer_list = []
        try:
            composer = Composer.objects.get(name=model_name)
        except ObjectDoesNotExist:
            composer = Composer(name=model_name,
                                birth_date=kwargs.get('birth_date'),
                                death_date=kwargs.get('death_date'),
                                created=datetime.datetime.now(),
                                updated=datetime.datetime.now())
            composer.save()
            if cleanup is not None:
                cleanup.list.append(composer)

        composer_list.append(composer)
        return composer_list

    if model_type == "Collection":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        collection_list = []
        for token in tokenized_inputs:
            try:
                collection = Collection.objects.get(title=token)
            except ObjectDoesNotExist:
                collection = Collection(title=token,
                                        public=kwargs.get('is_public'),
                                        creator=kwargs.get('creator'),
                                        created=datetime.datetime.now(),
                                        updated=datetime.datetime.now())
                collection.save()
                if cleanup is not None:
                    cleanup.list.append(collection)
            collection_list.append(collection)
        return collection_list

    if model_type == "Language":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        language_list = []
        for token in tokenized_inputs:
            try:
                language = Language.objects.get(name=token)
            except ObjectDoesNotExist:
                language = Language(name=token,
                                    created=datetime.datetime.now(),
                                    updated=datetime.datetime.now())
                language.save()
                if cleanup is not None:
                    cleanup.list.append(language)
            language_list.append(language)
        return language_list

    if model_type == "Location":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        location_list = []
        for token in tokenized_inputs:
            try:
                location = Location.objects.get(name=token)
            except ObjectDoesNotExist:
                location = Location(name=token,
                                    created=datetime.datetime.now(),
                                    updated=datetime.datetime.now())
                location.save()
                if cleanup is not None:
                    cleanup.list.append(location)
            location_list.append(location)
        return location_list

    if model_type == "Source":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        source_list = []
        for token in tokenized_inputs:
            try:
                source = Source.objects.get(name=token)
            except ObjectDoesNotExist:
                source = Source(name=token,
                                  created=datetime.datetime.now(),
                                  updated=datetime.datetime.now())
                source.save()
                if cleanup is not None:
                    cleanup.list.append(source)
            source_list.append(source)
        return source_list

    if model_type == "InstrumentVoice":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        instrument_list = []
        for token in tokenized_inputs:
            try:
                instrument = InstrumentVoice.objects.get(name=token)
            except ObjectDoesNotExist:
                instrument = InstrumentVoice(name=token,
                                             created=datetime.datetime.now(),
                                             updated=datetime.datetime.now())
                instrument.save()
                if cleanup is not None:
                    cleanup.list.append(instrument)
            instrument_list.append(instrument)
        return instrument_list


class Cleanup:
    def __init__(self):
        self.list = []

    def cleanup(self):
        for x in self.list:
            x.delete()
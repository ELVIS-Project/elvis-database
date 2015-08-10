import datetime
import json
import urllib2
import zipfile
import uuid
import shutil
import pytz
import os

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
from elvis.models import Genre
from elvis.models import InstrumentVoice
from elvis.models import Tag
from django.db.models import ObjectDoesNotExist
from difflib import SequenceMatcher

class Cleanup:
    """Keep track of created objects during an attempt to create a new piece. """

    def __init__(self):
        self.list = []

    def cleanup(self):
        """Delete all models created to support piece-creation."""
        for x in self.list:
            if x['new']:
                x['model'].delete()


def solr_suggest(request):
    """Query solr suggester for typeahead suggestions based on the contents of the database.
    :param request: Django request object with a 'q' parameter (the query) and a 'd' parameter (the name of the
        suggestion dictionary to query).
    :return: json-formatted list of the suggestions.
    """
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
                sorted_suggestions = sorted(data['suggestions'], key=lambda s: SequenceMatcher(None, value, s['term']).ratio(), reverse=True)
                for i in range(min(7,data['numFound'])):
                    results.append({'name': sorted_suggestions[i]['term']})
    j_results = json.dumps(results)
    return HttpResponse(j_results, content_type="application/json")


def upload_files(request, file_name, upload_path):
    """Upload files to a temporary directory, unzip any .zip files along the way.
    :param request: Django request object.
    :param file_name: Name of the multi-file input field in request.FILES to upload from.
    :param upload_path: The random filename in temp where the files will be uploaded.
    :return: List of dicts describing uploaded files.
    """

    files = []

    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp/')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp/'))
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    file_list = request.FILES.getlist(file_name)

    i = 1
    for f in file_list:
        # If the file has an accepted extension, upload it.
        if not any(f.name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and any(
                f.name.endswith(x) for x in settings.ELVIS_EXTENSIONS):
            new_name = f.name.replace('/', '-').encode('ascii', 'ignore')
            upload_file(f, os.path.join(upload_path, new_name))
            files.append({'name': new_name,
                          'uploader': request.user.username,
                          'path': upload_path})

        # Or, if the file is a zip file, upload, extract good files, then delete the archive.
        if f.name.endswith('.zip'):
            new_name = f.name.replace('/', '-').encode('ascii', 'ignore')
            upload_file(f, os.path.join(upload_path, new_name))
            try:
                unzipped_files = unzip_file(upload_path, new_name)
                for file_name in unzipped_files:
                    files.append({'name': file_name,
                                  'uploader': request.user.username,
                                  'path': upload_path})
            except zipfile.BadZipfile:
                files.append({'name': f.name, 'error': "Zip file could not be opened."})

    return files


def upload_file(mem_file, local_path):
    """Upload file in chunks.
    :param mem_file: In-memory file from request.FILES.
    :param local_path: Path to upload file to.
    """
    with open(local_path, 'wb+') as destination:
        for chunk in mem_file.chunks():
            destination.write(chunk)


def unzip_file(file_dir, file_name, **kwargs):
    """Unzip files with acceptable extensions to the archives directory.
    :param file_dir: Directory of the zip archive.
    :param file_name: Name of the zip archive.
    :param kwargs: -delete_after: Deletes the archive after extraction.
    :return:
    """
    files = []
    zipped_file = zipfile.ZipFile(os.path.join(file_dir, file_name), 'r')
    file_contents = zipped_file.namelist()

    i = 1
    for f_name in file_contents:
        if (not any(f_name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and
                any(f_name.endswith(x) for x in settings.ELVIS_EXTENSIONS) and
                not any(x in f_name for x in ('/', '\\'))):
            new_name = "{0}{1}.{2}".format("unzippedfile", str(i), f_name.rsplit('.')[-1])
            f = open(os.path.join(file_dir, new_name), 'wb+')
            f.write(zipped_file.open(f_name).read())
            files.append(new_name)
            i += 1

    zipped_file.close()

    return files


def handle_attachments(request, parent, cleanup, file_name, file_source):
    """Creates attachment objects for all files and links them with their parent
    :param request: Django request object.
    :param parent: The parent object to link attachments to.
    :param cleanup: Cleanup object.
    :param file_name: Name of the multi-file input field in request.FILES to upload from.
    :param file_source: The value for the source of the file.
    :return: List of attachment objects that are created.
    """

    upload_path = os.path.join(settings.MEDIA_ROOT, 'temp/', (uuid.uuid4().__str__() + '/'))
    results = []
    files = upload_files(request, file_name, upload_path)
    i = 1
    for f in files:
        att = Attachment()
        att.save()  # needed to create hash dir.
        cleanup.list.append({"model": att, "new": True})
        att.uploader = request.user
        new_name = "{0}_{1}_{2}.{3}".format(parent.title.replace(" ", "-"),
                                            parent.composer.name.replace(" ", "-"),
                                            "file" + str(i),
                                            f['name'].rsplit('.')[-1])
        new_name = new_name.replace('/', '-').encode('ascii', 'ignore')
        os.rename(os.path.join(f['path'], f['name']), os.path.join(f['path'], new_name))
        with open(os.path.join(f['path'], new_name), 'r+') as dest:
            file_content = File(dest)
            att.attachment.save(os.path.join(att.attachment_path, new_name), file_content)
        att.source = file_source
        att.save()
        results.append(att)
        os.remove(os.path.join(f['path'], new_name))
        i += 1

    for att in results:
        parent.attachments.add(att)

    parent.save()
    shutil.rmtree(upload_path)
    return results


def handle_dynamic_file_table(request, parent, table_name, cleanup=Cleanup()):
    """Upload all files and create all objects and relationships in a dynamic file table.
    :param request: Django request object.
    :param parent: The parent object to link movements/files to.
    :param table_name: The name of the dynamic table in the page template.
    :param cleanup: Cleanup object.
    :return: List of all objects created.
    """
    results = []
    attachments = []
    files = {}
    for item in request.POST:
        if item.startswith(table_name + "_title_") and request.POST[item]:
            file_name = request.POST[item]
            file_num = item[(len(table_name) + 7):]
            files[file_num] = file_name

    keys = files.keys()
    keys.sort()
    i = 1

    # Creating movements, then attaching files to them.
    for k in keys:
        mov_instrumentation_string = request.POST.get('mov' + k + "_instrumentation")
        mov_number_of_voices_string = request.POST.get('mov' + k + "_number_of_voices")
        mov_free_tags_string = request.POST.get('mov' + k + "_free_tags")
        mov_vocalization = request.POST.get('mov' + k + "_vocalization")
        mov_comment = request.POST.get('mov' + k + "_comment")
        mov_comment = request.POST.get('mov' + k + "_comment")
        new_mov = Movement(title=files[k],
                           position=i,
                           date_of_composition=parent.date_of_composition,
                           date_of_composition2=parent.date_of_composition2,
                           uploader=parent.uploader,
                           religiosity=parent.religiosity,
                           composer=parent.composer,
                           piece=parent)
        new_mov.save()
        for language in parent.languages.all():
            new_mov.languages.add(language)
        for genre in parent.genres.all():
            new_mov.genres.add(genre)
        for location in parent.locations.all():
            new_mov.locations.add(location)
        for source in parent.sources.all():
            new_mov.sources.add(source)
        for collection in parent.collections.all():
            new_mov.collections.add(collection)

        if mov_instrumentation_string:
            mov_instrumentation = abstract_model_factory(mov_instrumentation_string, "InstrumentVoice", cleanup)
            for x in mov_instrumentation:
                new_mov.instruments_voices.add(x)
        else:
            for x in parent.instruments_voices.all():
                new_mov.instruments_voices.add(x)

        if mov_free_tags_string:
            mov_free_tags = abstract_model_factory(mov_free_tags_string, "Tag", cleanup)
            for x in mov_free_tags:
                new_mov.tags.add(x)
        else:
            for x in parent.tags.all():
                new_mov.tags.add(x)

        if mov_number_of_voices_string:
            new_mov.number_of_voices = mov_number_of_voices_string
        else:
            new_mov.number_of_voices = parent.number_of_voices

        if mov_vocalization:
            new_mov.vocalization = mov_vocalization
        else:
            new_mov.vocalization = parent.vocalization

        if mov_comment:
            new_mov.comment = mov_comment

        file_keys = [x for x in request.POST.keys() if x.startswith('files_parent_')]
        file_numbers = [x.split('files_parent_')[-1] for x in file_keys if request.POST.get(x) == 'mov_title_' + k]
        for num in file_numbers:
            attachments.extend(handle_attachments(request, new_mov, cleanup, "files_files_" + num, request.POST.get('files_source_' + num)))
            request.POST.pop('files_source_' + num)
            request.POST.pop('files_parent_' + num)
            request.FILES.pop('files_files_' + num)
        request.POST.pop('mov_title_' + k)

        cleanup.list.append({"model": new_mov, "new": True})
        new_mov.save()
        results.append(new_mov)
        i += 1

    # Attaching files to piece.
    file_numbers = [x.split('files_parent_')[-1] for x in request.POST.keys() if request.POST.get(x) == 'piece']
    for num in file_numbers:
        attachments.extend(handle_attachments(request, parent, cleanup, "files_files_" + num, request.POST.get('files_source_' + num)))
    parent.save()
    results.extend(attachments)
    return results


def abstract_model_factory(model_name, model_type, cleanup=Cleanup(), **kwargs):
    """Find or create models from user-inputted text.
    :param model_name: Name or list of names of models to be found/created.
    :param model_type: Type of model(s) to find/create.
    :param cleanup: Cleanup object.
    :param kwargs:  -birth_date: Birth date for composer objects.
                    -death_date: Death date for composer objects.
                    -is_public: Boolean for collections.
                    -creator: Django user for objects that require a creator.
    :return: A list of dicts where l[index]['model'] = The model itself and l[index]['new'] = a bool saying whether the
            model was newly created or not.
    """
    if model_type == "Composer":
        composer_list = []
        try:
            composer = Composer.objects.get(name=model_name)
            cleanup.list.append({"model": composer, "new": False})
        except ObjectDoesNotExist:
            composer = Composer(name=model_name,
                                birth_date=kwargs.get('birth_date'),
                                death_date=kwargs.get('death_date'),
                                created=datetime.datetime.now(pytz.utc),
                                updated=datetime.datetime.now(pytz.utc))
            composer.save()
            cleanup.list.append({"model": composer, "new": True})

        composer_list.append(composer)
        return composer_list

    elif model_type == "Collection":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        collection_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    collection = Collection.objects.get(title=token)
                    cleanup.list.append({"model": collection, "new": False})
                except ObjectDoesNotExist:
                    collection = Collection(title=token,
                                            public=kwargs.get('is_public'),
                                            creator=kwargs.get('creator'),
                                            created=datetime.datetime.now(pytz.utc),
                                            updated=datetime.datetime.now(pytz.utc))
                    collection.save()
                    cleanup.list.append({"model": collection, "new": True})
                collection_list.append(collection)
        return collection_list

    elif model_type == "Language":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        language_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    language = Language.objects.get(name=token)
                    cleanup.list.append({"model": language, "new": False})
                except ObjectDoesNotExist:
                    language = Language(name=token,
                                        created=datetime.datetime.now(pytz.utc),
                                        updated=datetime.datetime.now(pytz.utc))
                    language.save()
                    cleanup.list.append({"model": language, "new": True})
                language_list.append(language)
        return language_list

    elif model_type == "Genre":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        genre_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    genre = Genre.objects.get(name=token)
                    cleanup.list.append({"model": genre, "new": False})
                except ObjectDoesNotExist:
                    genre = Genre(name=token,
                                  created=datetime.datetime.now(pytz.utc),
                                  updated=datetime.datetime.now(pytz.utc))
                    genre.save()
                    cleanup.list.append({"model": genre, "new": True})
                genre_list.append(genre)
        return genre_list

    elif model_type == "Location":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        location_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    location = Location.objects.get(name=token)
                    cleanup.list.append({"model": location, "new": False})
                except ObjectDoesNotExist:
                    location = Location(name=token,
                                        created=datetime.datetime.now(pytz.utc),
                                        updated=datetime.datetime.now(pytz.utc))
                    location.save()
                    cleanup.list.append({"model": location, "new": True})
                location_list.append(location)
        return location_list

    elif model_type == "Source":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        source_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    source = Source.objects.get(name=token)
                    cleanup.list.append({"model": source, "new": False})
                except ObjectDoesNotExist:
                    source = Source(name=token,
                                    created=datetime.datetime.now(pytz.utc),
                                    updated=datetime.datetime.now(pytz.utc))
                    source.save()
                    cleanup.list.append({"model": source, "new": True})
                source_list.append(source)
        return source_list

    elif model_type == "InstrumentVoice":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        instrument_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    instrument = InstrumentVoice.objects.get(name=token)
                    cleanup.list.append({"model": instrument, "new": False})
                except ObjectDoesNotExist:
                    instrument = InstrumentVoice(name=token,
                                                 created=datetime.datetime.now(pytz.utc),
                                                 updated=datetime.datetime.now(pytz.utc))
                    instrument.save()
                    cleanup.list.append({"model": instrument, "new": True})
                instrument_list.append(instrument)
        return instrument_list

    elif model_type == "Tag":
        tokenized_inputs = map((lambda x: x.strip()), model_name.rsplit(";"))
        tag_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    tag = Tag.objects.get(name=token)
                    cleanup.list.append({"model": tag, "new": False})
                except ObjectDoesNotExist:
                    tag = Tag(name=token)
                    tag.save()
                    cleanup.list.append({"model": tag, "new": True})
                tag_list.append(tag)
        return tag_list

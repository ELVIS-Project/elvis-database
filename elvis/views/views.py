import datetime
import ujson as json
import urllib.request, urllib.parse, urllib.error
import zipfile
import uuid
import shutil
import pytz
import os
import re

from difflib import SequenceMatcher
from django.http import HttpResponse
from django.conf import settings
from django.db.models import ObjectDoesNotExist

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
from urllib.parse import unquote


class Cleanup:
    """Keep track of created objects during an attempt to create a new
    piece. """

    def __init__(self):
        self.list = []

    def cleanup(self):
        """Delete all models created to support piece-creation."""
        for x in self.list:
            if x['isNew']:
                x['object'].delete()


def solr_suggest(request):
    """Query solr suggester for typeahead-style suggestions based on the
    contents of the database.
    :param request: Django request object with a 'q' parameter (the query)
    and a 'd' parameter (the name of the suggestion dictionary to query).
    :return: json-formatted list of the suggestions.
    """
    results = []

    if request.method == "GET" and 'q' in request.GET and 'd' in request.GET:
        value = request.GET['q']
        dictionary = request.GET['d']
        if len(value) < 1:
            return False
        if dictionary == "generalSuggest":
            url = settings.SOLR_SERVER + \
                "/suggest/?wt=json&suggest.dictionary=pieceSuggest" \
                "&suggest.dictionary=composerSuggest" \
                "&suggest.dictionary=collectionSuggest" \
                "&q={1}".format(dictionary, value)
            json_string = urllib.request.urlopen(url)
            json_dict = json.loads((json_string.read()).decode('utf-8'))

            value = unquote(value)
            piece_suggestions = json_dict['suggest']['pieceSuggest'][value]
            comp_suggestions = json_dict['suggest']['composerSuggest'][value]
            coll_suggestions = json_dict['suggest']['collectionSuggest'][value]
            all_suggestions = []

            if piece_suggestions['numFound']:
                all_suggestions = piece_suggestions['suggestions']
            if comp_suggestions['numFound']:
                if all_suggestions:
                    all_suggestions.extend(comp_suggestions['suggestions'])
                else:
                    all_suggestions = comp_suggestions['suggestions']
            if coll_suggestions['numFound']:
                if all_suggestions:
                    all_suggestions.extend(coll_suggestions['suggestions'])
                else:
                    all_suggestions = coll_suggestions['suggestions']
            if all_suggestions:
                sorted_suggestions = sorted(all_suggestions,
                                            key=lambda s: _seq(s, value),
                                            reverse=True)
                for i in range(min(7, len(sorted_suggestions))):
                    results.append({'name': sorted_suggestions[i]['term']})
        else:
            url = settings.SOLR_SERVER + "/suggest/?wt=json" \
                                             "&suggest.dictionary={0}" \
                                             "&q={1}".format(dictionary, value)
            json_string = urllib.request.urlopen(url)
            resp = json.loads((json_string.read()).decode('utf-8'))
            resp = resp['suggest']['{0}'.format(dictionary)]
            data = resp[list(resp.keys())[0]]
            if data['numFound'] > 0:
                sorted_suggestions = sorted(data['suggestions'],
                                            key=lambda s: _seq(s, value),
                                            reverse=True)
                for i in range(min(7, data['numFound'])):
                    results.append({'name': sorted_suggestions[i]['term']})
    j_results = json.dumps(results)
    return HttpResponse(j_results, content_type="application/json")

def _seq(s, v):
    """Return a num representing the results likeness to the query.
       For use in solr_suggest"""
    return SequenceMatcher(None, v, s['term']).ratio()


def upload_files(request, file_name, upload_path):
    """Upload files to a temporary directory, unzip any .zip files along the
    way.
    :param request: Django request object.
    :param file_name: Name of the multi-file input field in request.FILES to
    upload from.
    :param upload_path: The random filename in temp where the files will be
    uploaded.
    :return: List of dicts describing uploaded files.
    """

    files = []

    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'temp/')):
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'temp/'))
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    file_list = request.FILES.getlist(file_name)

    for f in file_list:
        # If the file has an accepted extension, upload it.
        if not any(f.name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) \
                and any(f.name.endswith(x) for x in settings.ELVIS_EXTENSIONS):
            new_name = f.name.replace(" ", "-")
            upload_file(f, os.path.join(upload_path, new_name))
            files.append({
                'name': new_name,
                'uploader': request.user.username,
                'path': upload_path})

        # Or, if the file is a zip file, upload, extract good files,
        # then delete the archive.
        if f.name.endswith('.zip'):
            new_name = f.name.replace('/', '-').encode('ascii', 'ignore')
            upload_file(f, os.path.join(upload_path, new_name))
            try:
                unzipped_files = unzip_file(upload_path, new_name)
                for file_name in unzipped_files:
                    files.append({'name': file_name, 'uploader': request.user.username,
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


def unzip_file(file_dir, file_name):
    """Unzip files with acceptable extensions to the archives directory.
    :param file_dir: Directory of the zip archive.
    :param file_name: Name of the zip archive.
    :return: A list of files that have been created in file_dir
    """
    files = []
    zipped_file = zipfile.ZipFile(os.path.join(file_dir, file_name), 'r')
    file_contents = zipped_file.namelist()

    i = 1
    for f_name in file_contents:
        if (not any(f_name.startswith(x) for x in settings.ELVIS_BAD_PREFIX) and any(
                f_name.endswith(x) for x in settings.ELVIS_EXTENSIONS) and not any(
                x in f_name for x in ('/', '\\'))):
            new_name = "{0}{1}.{2}".format("unzippedfile", str(i), f_name.rsplit('.')[-1])
            f = open(os.path.join(file_dir, new_name), 'wb+')
            f.write(zipped_file.open(f_name).read())
            files.append(new_name)
            i += 1

    zipped_file.close()

    return files


def handle_attachments(request, parent, cleanup, file_field, file_source):
    """Creates attachment objects for all files and links them with their parent
    :param request: Django request object.
    :param parent: The parent object to link attachments to.
    :param cleanup: Cleanup object.
    :param file_field: Name of the multi-file input field in request.FILES to
    upload from.
    :param file_source: The value for the source of the file.
    :return: List of attachment objects that are created.
    """

    upload_path = os.path.join(settings.MEDIA_ROOT, 'temp/', (uuid.uuid4().__str__() + '/'))
    results = []
    files = upload_files(request, file_field, upload_path)
    i = parent.attachments.all().count() + 1
    for f in files:
        att = Attachment()
        att.save()  # needed to create hash dir.
        cleanup.list.append({"object": att, "isNew": True})
        att.creator = request.user
        att.attach_file(f['path'], f['name'], parent, number=i, source=file_source)
        results.append(att)
        i += 1

    for att in results:
        parent.attachments.add(att)

    shutil.rmtree(upload_path)
    return results


def handle_dynamic_file_table(request, parent, cleanup=Cleanup()):
    """Upload all files and create all objects and relationships in a
    dynamic file table.
    :param request: Django request object.
    :param parent: The parent object to link movements/files to.
    :param cleanup: Cleanup object.
    :return: List of all objects created.
    """
    results = []
    attachments = []
    files = {}
    for item in request.POST:
        if item.startswith("mov_title_") and request.POST[item]:
            file_name = request.POST[item]
            file_num = int(re.findall(r'\d+', item)[0])
            files[file_num] = file_name

    keys = list(files.keys())
    keys.sort()

    # Renumber existing movements before adding more.
    i = 1
    for mov in parent.movements.all():
        mov.position = i
        mov.save()
        i += 1

    # Creating movements, then attaching files to them.
    for k in keys:
        mov_instrumentation_string = request.POST.get('mov' + str(k) + "_instrumentation")
        mov_number_of_voices_string = request.POST.get('mov' + str(k) + "_number_of_voices")
        mov_free_tags_string = request.POST.get('mov' + str(k) + "_free_tags")
        mov_vocalization = request.POST.get('mov' + str(k) + "_vocalization")
        mov_comment = request.POST.get('mov' + str(k) + "_comment")
        new_mov = Movement(title=files[k], position=i,
                           composition_start_date=parent.composition_start_date,
                           composition_end_date=parent.composition_end_date,
                           creator=parent.creator, religiosity=parent.religiosity,
                           composer=parent.composer, piece=parent)
        new_mov.save()
        for language in parent.languages.all():
            new_mov.languages.add(language)
        for genre in parent.genres.all():
            new_mov.genres.add(genre)
        for location in parent.locations.all():
            new_mov.locations.add(location)
        for source in parent.sources.all():
            new_mov.sources.add(source)

        if mov_instrumentation_string:
            mov_instrumentation = abstract_model_factory(mov_instrumentation_string,
                                                         "InstrumentVoice", cleanup)
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

        file_keys = [x for x in list(request.POST.keys()) if x.startswith('files_parent_')]
        file_numbers = [x.split('files_parent_')[-1] for x in file_keys if
                        request.POST.get(x) == 'mov_title_' +str(k)]
        for num in file_numbers:
            attachments.extend(handle_attachments(request, new_mov, cleanup, "files_files_" + num,
                                                  request.POST.get('files_source_' + num)))
            request.POST.pop('files_source_' + num)
            request.POST.pop('files_parent_' + num)
            request.FILES.pop('files_files_' + num)
        request.POST.pop('mov_title_' +str(k))

        cleanup.list.append({"object": new_mov, "isNew": True})
        new_mov.save()
        results.append(new_mov)
        i += 1

    # Attaching other files.
    file_numbers = [x for x in list(request.POST.keys()) if x.startswith('files_parent_')]
    for postfile in file_numbers:
        if request.POST.get(postfile) == 'piece':
            # This attaches files to the piece itself - is pretty
            # straightforward.
            num = postfile.split('files_parent_')[-1]
            attachments.extend(handle_attachments(request, parent, cleanup, "files_files_" + num,
                                                  request.POST.get('files_source_' + num)))
        else:
            """
            This attaches new files to an existing movement and is *very* hacky.
            It finds the html-id of the row of the movement table it is
            attached to (request.POST.get(postfile)), then parses
            the number of that movement-id, then attaches to the [n-1]'th
            movement of the piece.
            This works because:
                ->The id's assigned to movements rows by javascript go from
                    1-[piece.attachments.length+1]
                ->The ordering on the frontend is based on the ordering in the backend
                ->It is impossible to insert a new movement between existing
                    movements: the movement table works like a stack.
                ->Even if an existing movement is to be deleted (therby throwing off the count),
                    the deletion step will occour *after* this step.
            By the above logic, the [n-1]'th movement in the table on the
            frontend will be the n'th movement on the backend - so this works.
            """
            movnum = int(re.findall(r'\d+', request.POST.get(postfile))[0])
            mov = parent.movements.all()[movnum - 1]
            num = postfile.split('files_parent_')[-1]
            mov.save()
            attachments.extend(handle_attachments(request, mov, cleanup, "files_files_" + num,
                                                  request.POST.get('files_source_' + num)))

    results.extend(attachments)
    return results


def abstract_model_factory(object_name, object_type, cleanup=Cleanup(), **kwargs):
    """Find or create models from user-inputted text.

    :param object_name: Name or list of names of models to be found/created.
    :param object_type: Type of model(s) to find/create.
    :param cleanup: Cleanup object.
    kwargs:
        birth_date: Birth date for composer objects.
        death_date: Death date for composer objects.
        creator: Django user for objects that require a creator.
    :return: A list of dicts of the form [{object: x, isNew: y}], where
        object is the object created, and isNew describes if it was created (True)
        or found (False)

    where l[index]['model'] = The model itself and
    l[index]['new'] = a bool saying whether the model was newly created or not.
    """
    if object_type == "Composer":
        composer_list = []
        try:
            composer = Composer.objects.get(title=object_name)
            cleanup.list.append({"object": composer, "isNew": False})
        except ObjectDoesNotExist:
            composer = Composer(title=object_name, birth_date=kwargs.pop('birth_date'),
                                death_date=kwargs.pop('death_date'),
                                created=datetime.datetime.now(pytz.utc),
                                updated=datetime.datetime.now(pytz.utc))
            composer.save()
            cleanup.list.append({"object": composer, "isNew": True})

        composer_list.append(composer)
        return composer_list

    elif object_type == "Collection":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        collection_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    collection = Collection.objects.get(title=token)
                    cleanup.list.append({"object": collection, "isNew": False})
                except ObjectDoesNotExist:
                    collection = Collection(title=token, public=True,
                                            creator=kwargs.get('creator'),
                                            created=datetime.datetime.now(pytz.utc),
                                            updated=datetime.datetime.now(pytz.utc))
                    collection.save()
                    cleanup.list.append({"object": collection, "isNew": True})
                collection_list.append(collection)
        return collection_list

    elif object_type == "Language":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        language_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    language = Language.objects.get(title=token)
                    cleanup.list.append({"object": language, "isNew": False})
                except ObjectDoesNotExist:
                    language = Language(title=token, created=datetime.datetime.now(pytz.utc),
                                        updated=datetime.datetime.now(pytz.utc))
                    language.save()
                    cleanup.list.append({"object": language, "isNew": True})
                language_list.append(language)
        return language_list

    elif object_type == "Genre":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        genre_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    genre = Genre.objects.get(title=token)
                    cleanup.list.append({"object": genre, "isNew": False})
                except ObjectDoesNotExist:
                    genre = Genre(title=token, created=datetime.datetime.now(pytz.utc),
                                  updated=datetime.datetime.now(pytz.utc))
                    genre.save()
                    cleanup.list.append({"object": genre, "isNew": True})
                genre_list.append(genre)
        return genre_list

    elif object_type == "Location":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        location_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    location = Location.objects.get(title=token)
                    cleanup.list.append({"object": location, "isNew": False})
                except ObjectDoesNotExist:
                    location = Location(title=token, created=datetime.datetime.now(pytz.utc),
                                        updated=datetime.datetime.now(pytz.utc))
                    location.save()
                    cleanup.list.append({"object": location, "isNew": True})
                location_list.append(location)
        return location_list

    elif object_type == "Source":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        source_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    source = Source.objects.get(title=token)
                    cleanup.list.append({"object": source, "isNew": False})
                except ObjectDoesNotExist:
                    source = Source(title=token, created=datetime.datetime.now(pytz.utc),
                                    updated=datetime.datetime.now(pytz.utc))
                    source.save()
                    cleanup.list.append({"object": source, "isNew": True})
                source_list.append(source)
        return source_list

    elif object_type == "InstrumentVoice":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        instrument_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    instrument = InstrumentVoice.objects.get(title=token)
                    cleanup.list.append({"object": instrument, "isNew": False})
                except ObjectDoesNotExist:
                    instrument = InstrumentVoice(title=token,
                                                 created=datetime.datetime.now(pytz.utc),
                                                 updated=datetime.datetime.now(pytz.utc))
                    instrument.save()
                    cleanup.list.append({"object": instrument, "isNew": True})
                instrument_list.append(instrument)
        return instrument_list

    elif object_type == "Tag":
        tokenized_inputs = list(map((lambda x: x.strip()), object_name.rsplit(";")))
        tag_list = []
        for token in tokenized_inputs:
            if token != "":
                try:
                    tag = Tag.objects.get(title=token)
                    cleanup.list.append({"object": tag, "isNew": False})
                except ObjectDoesNotExist:
                    tag = Tag(title=token)
                    tag.save()
                    cleanup.list.append({"object": tag, "isNew": True})
                tag_list.append(tag)
        return tag_list

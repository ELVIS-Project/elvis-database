import datetime
import json

import pytz
from django.views.decorators.csrf import csrf_protect
from rest_framework import generics
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.attachment import Attachment
from elvis.forms import PieceForm
from elvis.tasks import rebuild_suggester_dicts
from elvis.views.views import abstract_model_factory
from elvis.views.views import handle_dynamic_file_table
from elvis.views.views import Cleanup
from elvis.views.common import ElvisDetailView, ElvisListCreateView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from elvis.serializers import PieceFullSerializer, PieceListSerializer


class PieceListHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_list.html"


class PieceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_detail.html"


class PieceCreateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_create.html"


class PieceUpdateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_update.html"


class PieceDetail(ElvisDetailView):
    serializer_class = PieceFullSerializer
    renderer_classes = (PieceDetailHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    def patch(self, request, *args, **kwargs):
        if self.is_authorized(request, *args, **kwargs)['can_edit']:
            return piece_update(request, *args, **kwargs)


class PieceCreate(generics.RetrieveAPIView):
    renderer_classes = (PieceCreateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return Response(status=status.HTTP_200_OK)
        else:
            return HttpResponseRedirect('/login/?error=upload')


class PieceUpdate(generics.RetrieveAPIView):
    serializer_class = PieceFullSerializer
    renderer_classes = (PieceUpdateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)
    queryset = Piece.objects.all()


class PieceList(ElvisListCreateView):
    serializer_class = PieceListSerializer
    renderer_classes = (PieceListHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

    def post(self, request, *args, **kwargs):
        return piece_create(request, *args, **kwargs)


def piece_create(request, *args, **kwargs):
    form = validateDynamicForm(request, PieceForm(request.POST))
    if not form.is_valid():
        # Form errors are rendered for user on the front end.
        data = {'errors': form.errors}
        return HttpResponse(content=data, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)

    clean = Cleanup()
    clean_form = form.cleaned_data
    new_piece = Piece(title=clean_form['title'],
                      creator=request.user,
                      created=datetime.datetime.now(pytz.utc),
                      updated=datetime.datetime.now(pytz.utc))
    clean.list.append({"object": new_piece, "isNew": True})
    try:
        new_piece.save()
    except:
        clean.cleanup()
        raise

    object_list = []
    for key in clean_form:
        object_list.append({'id': key, 'value': clean_form[key]})
    handle_related_models(object_list, new_piece, clean,
                          user=request.user, birth_date=clean_form['composer_birth_date'],
                          death_date=clean_form['composer_death_date'])

    handle_dynamic_file_table(request, new_piece, clean)
    rebuild_suggester_dicts.delay()
    data = json.dumps({'success': True, 'id': new_piece.id,
                       'url': "/piece/{0}".format(new_piece.id)})
    return HttpResponse(data, content_type="application/json", status=status.HTTP_201_CREATED)


def piece_update(request, *args, **kwargs):
    # Update a piece based on a dict of changes in request.POST['changes']
    patch_data = request.data
    form = validateDynamicForm(request, PieceForm(patch_data))
    if not form.is_valid():
        # Form errors are rendered for user on the front end. Collection
        # validation errors are ignored, as these cannot be modified from
        # the update page.
        if form.errors.get('collections'):
            del form.errors['collections']
        if form.errors:
            data = json.dumps({"errors": form.errors})
            return HttpResponse(content=data, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)

    clean = Cleanup()
    piece = Piece.objects.get(id=int(kwargs['pk']))
    change = json.loads(patch_data['changes'])

    """
    Creating new movements must occur before old movements are deleted,
    as the attachment of files depends on the ordering and numbering
    of movements in the piece's present state. See comment in
    handle_dynamic_file_table() for more information.
    """
    handle_dynamic_file_table(request, piece, clean)

    modify_movements = [x for x in change['modify'] if x['type'] == "M"]
    if modify_movements:
        for item in modify_movements:
            mov = Movement.objects.filter(id=item['id'])
            if not mov:
                break
            mov = mov[0]
            if item.get('tags'):
                tag_list = abstract_model_factory(item['tags'], "Tag", clean)
                mov.tags.clear()
                for x in tag_list:
                    mov.tags.add(x)
            if item.get('instruments_voices'):
                ins_list = abstract_model_factory(item['instruments_voices'], "InstrumentVoice", clean)
                mov.instruments_voices.clear()
                for x in ins_list:
                    mov.instruments_voices.add(x)
            if item.get('comment'):
                mov.comment = item['comment']
            if item.get('number_of_voices'):
                mov.number_of_voices = int(item['number_of_voices'])
            if item.get('vocalization'):
                mov.vocalization = item['vocalization']
            if item.get('title'):
                mov.title = item['title']

            mov.save()

    movement_positions = [x for x in change['modify'] if x['type'] == "M" and x.get('position')]
    movement_positions.extend([x for x in change['add'] if x['type'] == "M" and x.get('position')])
    if movement_positions:
        movements = piece.movements.all()
        for item in movement_positions:
            if item.get('id'):
                mov = movements.get(id=item['id'])
                mov.position = item['position']
                mov.save()
            elif item.get('name'):
                mov = movements.get(title=item['name'])
                mov.position = item['position']
                mov.save()

    modify_atts = [x for x in change['modify'] if x['type'] == "A"]
    if modify_atts:
        for item in modify_atts:
            att = Attachment.objects.filter(pk=item['id'])
            if not att:
                break
            att = att[0]
            if item.get('parent'):
                if item.get('newParentTitle') == "Attach to Piece":
                    att.movements.clear()
                    att.pieces.clear()
                    att.pieces.add(piece)
                    att.save()
                else:
                    mov = piece.movements.filter(title=item['newParentTitle'])
                    if not mov:
                        break
                    mov = mov[0]
                    att.movements.clear()
                    att.pieces.clear()
                    att.movements.add(mov)
                    att.save()
            if item.get('source'):
                att.source = item.get('source')
                att.save()

    modify_piece = [x for x in change['modify'] if x['type'] == "F"]
    if modify_piece:
        # Can use the same function as the piece-create here.
        handle_related_models(modify_piece, piece, clean)

    delete_attachments = [x for x in change['delete'] if x['type'] == "A"]
    if delete_attachments:
        for item in delete_attachments:
            att = Attachment.objects.filter(pk=item['id'])[0]
            if att:
                att.delete()
                
    delete_movements = [x for x in change['delete'] if x['type'] == "M"]
    if delete_movements:
        for item in delete_movements:
            mov = Movement.objects.filter(pk=item['id'])[0]
            if mov:
                mov.delete()


    data = json.dumps({'success': True, 'id': piece.id, 'url': "/piece/{0}".format(piece.id)})
    return HttpResponse(data, content_type="json")

def handle_related_models(object_list, parent, clean, **kwargs):
    """ Create/find and attach all related models for a piece.
    :param object_list: The list of objects to create/find, and which
     field they belong to, in the format [{id: field_name, value: x},]
    :param parent: The object to relate to.
    :param clean: A Cleanup object.
    :kwargs
            creator: the creator of the piece, taken from request.user
            birth_date: The birth-date of a composer object
            death_date: The death-date of a composer object
    :return:
    """
    for item in object_list:
        field = item.get('id')
        if field == "title":
            parent.title = item.get('value')
            continue
        if field == "composer":
            birth_date = kwargs.pop('birth_date', None)
            death_date = kwargs.pop('death_date', None)
            try:
                composer_list = abstract_model_factory(item.get('value'), "Composer", clean,
                                                       birth_date=birth_date,
                                                       death_date=death_date)
                composer = composer_list[0]
                parent.composer = composer
                continue
            except:
                clean.cleanup()
                raise
        if field == "collections":
            user = kwargs.pop('user', None)
            try:
                collection_list = abstract_model_factory(item.get('value'), "Collection", clean,
                                                         creator=user)
                for x in collection_list:
                    parent.collections.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "languages":
            try:
                language_list = abstract_model_factory(item.get('value'), "Language", clean)
                parent.languages.clear()
                for x in language_list:
                    parent.languages.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "locations":
            try:
                location_list = abstract_model_factory(item.get('value'), "Location", clean)
                parent.locations.clear()
                for x in location_list:
                    parent.locations.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "sources":
            try:
                source_list = abstract_model_factory(item.get('value'), "Source", clean)
                parent.sources.clear()
                for x in source_list:
                    parent.sources.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "tags":
            try:
                tag_list = abstract_model_factory(item.get('value'), "Tag", clean)
                parent.tags.clear()
                for x in tag_list:
                    parent.tags.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "genres":
            try:
                genre_list = abstract_model_factory(item.get('value'), "Genre", clean)
                parent.genres.clear()
                for x in genre_list:
                    parent.genres.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "instruments_voices":
            try:
                ins_list = abstract_model_factory(item.get('value'), "InstrumentVoice", clean)
                parent.instruments_voices.clear()
                for x in ins_list:
                    parent.instruments_voices.add(x)
                continue
            except:
                clean.cleanup()
                raise
        if field == "number_of_voices":
            parent.number_of_voices = int(item.get('value'))
        if field == "vocalization":
            parent.vocalization = item.get('value')
        if field == "religiosity":
            parent.religiosity = item.get('value')
        if field == "composition_start_date" and item.get('value'):
            parent.composition_start_date = int(item.get('value'))
        if field == "composition_end_date" and item.get('value'):
            parent.composition_end_date = int(item.get('value'))
        if field == "comment":
            parent.comment = item.get('value')
    parent.save()
    rebuild_suggester_dicts.delay()
    data = json.dumps({'success': True, 'id': parent.id,
                       'url': "/piece/{0}".format(parent.id)})
    return HttpResponse(data, content_type="json")

def validateDynamicForm(request, form):
    form.is_valid()
    movement_title_list = [x for x in list(request.POST.keys()) if x.startswith('_existingmov_title_')]
    for mov in movement_title_list:
        if not request.POST.get(mov):
            form.add_error(None, [mov, "Movements require a title."])

    file_source_list = [x for x in list(request.POST.keys()) if x.startswith('files_source')]
    for source in file_source_list:
        if request.FILES.get(source.replace('source', 'files')) and not request.POST.get(source):
            form.add_error(None, [source, "Files require a source!"])
            
    return form
import datetime
import json

import pytz
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer, PieceListSerializer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.attachment import Attachment
from elvis.forms import PieceForm
from elvis.elvis.tasks import rebuild_suggester_dicts
from elvis.views.views import abstract_model_factory
from elvis.views.views import handle_dynamic_file_table
from elvis.views.views import Cleanup
from django.utils.decorators import method_decorator
from django.http import HttpResponse


class PieceListHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_list.html"


class PieceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_detail.html"


class PieceCreateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_create.html"

class PieceUpdateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_update.html"



class PieceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceDetailHTMLRenderer)
    queryset = Piece.objects.all()

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(PieceDetail, self).get(self, request)

        response = super(PieceDetail, self).get(self, request)
        user_download = request.user.downloads.all()[0]

        if user_download.collection_pieces.filter(pk=response.data['item_id']):
            response.data['in_cart'] = True
            for i in range(len(response.data['movements'])):
                response.data['movements'][i]['in_cart'] = 'Piece'
        else:
            response.data['in_cart'] = False
            for i in range(len(response.data['movements'])):
                mov_pk = response.data['movements'][i]['item_id']
                if user_download.collection_movements.filter(pk=mov_pk):
                    response.data['movements'][i]['in_cart'] = True
                else:
                    response.data['movements'][i]['in_cart'] = False

        piece = Piece.objects.get(pk=response.data['item_id'])

        if piece.uploader == user:
            response.data['can_edit'] = True

        return response


class PieceCreate(generics.GenericAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceCreateHTMLRenderer)
    queryset = Piece.objects.all()

    def get(self, request, *args, **kwargs):
        if User.is_authenticated(request.user):
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class PieceUpdate(generics.RetrieveUpdateDestroyAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceUpdateHTMLRenderer)
    queryset = Piece.objects.all()

    def get(self, request, *args, **kwargs):
        piece = Piece.objects.get(pk=int(kwargs['pk']))
        if not piece or (piece.uploader != request.user
                         and not request.user.is_superuser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super(PieceUpdate, self).get(self, request, *args, **kwargs)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            piece = Piece.objects.get(id=request.POST['delete'])
            if not (request.user == piece.uploader or request.user.is_superuser):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            piece.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        return update(request, *args, **kwargs)

class PieceList(generics.ListCreateAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceListSerializer
    renderer_classes = (JSONRenderer, PieceListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Piece.objects.all()

    def get_queryset(self):
        query = self.request.GET.get('creator', None)
        if query:
            return Piece.objects.filter(uploader__username=query)
        else:
            return Piece.objects.all()

    # Inserting a flag that specifies if the piece is currently in the users' cart
    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return super(PieceList, self).get(self, request)

        response = super(PieceList, self).get(self, request)
        user_download = request.user.downloads.all()[0]
        for i in range(len(response.data['results'])):
            piece_pk = response.data['results'][i]['item_id']
            if user_download.collection_pieces.filter(pk=piece_pk):
                response.data['results'][i]['in_cart'] = True
            else:
                response.data['results'][i]['in_cart'] = False
        return response

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        if 'delete' in request.POST:
            import pdb
            pdb.set_trace()
            piece = Piece.objects.get(id=request.POST['delete'])
            if not (request.user == piece.uploader or request.user.is_superuser):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            piece.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return create(request, *args, **kwargs)

def create(request, *args, **kwargs):
    if not request.user.is_active:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    form = PieceForm(request.POST)
    if not form.is_valid():
        data = json.dumps({'errors': form.errors})
        return HttpResponse(data, content_type="json")

    clean = Cleanup()
    clean_form = form.cleaned_data
    new_piece = Piece(title=clean_form['title'],
                      date_of_composition=clean_form[
                          'composition_start_date'],
                      date_of_composition2=clean_form[
                          'composition_end_date'],
                      religiosity=clean_form['religiosity'],
                      vocalization=clean_form['vocalization'],
                      uploader=request.user,
                      created=datetime.datetime.now(pytz.utc),
                      updated=datetime.datetime.now(pytz.utc))
    new_piece.save()
    clean.list.append({"model": new_piece, "new": True})

    if clean_form['number_of_voices']:
        new_piece.number_of_voices = int(clean_form['number_of_voices'])
    if clean_form['comment']:
        new_piece.comment = clean_form['comment']

    try:
        composer_list = abstract_model_factory(clean_form['composer'],
                                               "Composer", clean,
                                               birth_date=clean_form[
                                                   'composer_birth_date'],
                                               death_date=clean_form[
                                                   'composer_death_date'])
        composer = composer_list[0]
        new_piece.composer = composer
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['collections']:
            collection_list = abstract_model_factory(
                clean_form['collections'], "Collection", clean,
                is_public=True, creator=request.user)
            for x in collection_list:
                new_piece.collections.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['languages']:
            language_list = abstract_model_factory(clean_form['languages'],
                                                   "Language", clean)
            for x in language_list:
                new_piece.languages.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['genres']:
            genre_list = abstract_model_factory(clean_form['genres'],
                                                "Genre", clean)
            for x in genre_list:
                new_piece.genres.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['locations']:
            location_list = abstract_model_factory(clean_form['locations'],
                                                   "Location", clean)
            for x in location_list:
                new_piece.locations.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['sources']:
            source_list = abstract_model_factory(clean_form['sources'],
                                                 "Source", clean)
            for x in source_list:
                new_piece.sources.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['tags']:
            tag_list = abstract_model_factory(clean_form['tags'], "Tag",
                                              clean)
            for x in tag_list:
                new_piece.tags.add(x)
    except:
        clean.cleanup()
        raise
    try:
        if clean_form['instruments_voices']:
            instrument_list = abstract_model_factory(
                clean_form['instruments_voices'], "InstrumentVoice", clean)
            for x in instrument_list:
                new_piece.instruments_voices.add(x)
    except:
        clean.cleanup()
        raise

    new_piece.save()
    try:
        handle_dynamic_file_table(request, new_piece, "mov", clean)
    except:
        clean.cleanup()
        raise

    new_piece.save()
    rebuild_suggester_dicts.delay()
    data = json.dumps({'success': True, 'id': new_piece.id,
                       'url': "/piece/{0}".format(new_piece.id)})
    return HttpResponse(data, content_type="json")

def update(request, *args, **kwargs):
    clean = Cleanup()
    piece = Piece.objects.get(pk=int(kwargs['pk']))
    change = json.loads(request.POST.get('changes'))

    handle_dynamic_file_table(request, piece, "mov", clean)

    if change.get('modify'):
        modify_movements = [x for x in change['modify'] if x['type'] == "M"]
        if modify_movements:
            for item in modify_movements:
                mov = Movement.objects.filter(pk=item['id'])
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
                mov.save()

    modify_atts = [x for x in change['modify'] if x['type'] == "A"]
    if modify_atts:
        for item in modify_atts:
            att = Attachment.objects.filter(pk=item['id'])
            if not att:
                break
            att = att[0]
            if item.get('parent'):
                if item.get('parent') == "piece":
                    att.movements.clear()
                    att.pieces.clear()
                    att.pieces.add(piece)
                    att.save()
                else:
                    mov = piece.movements.filter(title=item['newParent'])
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
        for item in modify_piece:
            id = item.get('id')
            if id == "title":
                piece.title = item.get('value')
                continue
            if id == "composer":
                try:
                    composer_list = abstract_model_factory(item.get('value'),
                                           "Composer", clean)
                    composer = composer_list[0]
                    piece.composer = composer
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "collections":
                try:
                    collection_list = abstract_model_factory(
                        item.get('value'), "Collection", clean,
                        is_public=True, creator=request.user)
                    for x in collection_list:
                        piece.collections.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "languages":
                try:
                    language_list = abstract_model_factory(
                        item.get('value'), "Language", clean)
                    piece.languages.clear()
                    for x in language_list:
                        piece.languages.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "locations":
                try:
                    location_list = abstract_model_factory(
                        item.get('value'), "Location", clean)
                    piece.locations.clear()
                    for x in location_list:
                        piece.locations.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "sources":
                try:
                    source_list = abstract_model_factory(
                        item.get('value'), "Source", clean)
                    piece.sources.clear()
                    for x in source_list:
                        piece.sources.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "tags":
                try:
                    tag_list = abstract_model_factory(
                        item.get('value'), "Tag", clean)
                    piece.tags.clear()
                    for x in tag_list:
                        piece.tags.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "genres":
                try:
                    genre_list = abstract_model_factory(
                        item.get('value'), "Genre", clean)
                    piece.genres.clear()
                    for x in genre_list:
                        piece.genres.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "instruments_voices":
                try:
                    ins_list = abstract_model_factory(
                        item.get('value'), "InstrumentVoice", clean)
                    piece.instruments_voices.clear()
                    for x in ins_list:
                        piece.instruments_voices.add(x)
                    continue
                except:
                    clean.cleanup()
                    raise
            if id == "number_of_voices":
                piece.number_of_voices = int(item.get('value'))
                continue
            if id == "date_of_composition":
                piece.date_of_composition = int(item.get('value'))
            if id == "date_of_composition2":
                piece.date_of_composition2 = int(item.get('value'))
            if id == "comment":
                piece.comment = item.get('value')
    piece.save()

    if change.get('delete'):
        delete_movements = [x for x in change['delete'] if x['type'] == "M"]
        if delete_movements:
            for item in delete_movements:
                mov = Movement.objects.filter(pk=item['id'])[0]
                if mov:
                    mov.delete()
        delete_attachments = [x for x in change['delete'] if x['type'] == "A"]
        if delete_attachments:
            for item in delete_attachments:
                att = Attachment.objects.filter(pk=item['id'])[0]
                if att:
                    att.delete()

    data = json.dumps({'success': True, 'id': piece.id,
                       'url': "/piece/{0}".format(piece.id)})
    return HttpResponse(data, content_type="json")




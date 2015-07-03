from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
import datetime
import pytz
import pdb
import json
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer
from elvis.models.piece import Piece
from elvis.forms import PieceForm

from elvis.views.views import abstract_model_factory, rebuild_suggester_dicts, handle_dynamic_file_table, Cleanup
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect, HttpResponse


class PieceListHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_list.html"


class PieceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_detail.html"


class PieceCreateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_create.html"


class PieceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceDetailHTMLRenderer)
    queryset = Piece.objects.all()


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


class PieceList(generics.ListCreateAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceListHTMLRenderer)
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Piece.objects.all()

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        form = PieceForm(request.POST)
        if not form.is_valid():
            data = json.dumps({'errors': form.errors})
            return HttpResponse(data, content_type="json")

        clean = Cleanup()
        clean_form = form.cleaned_data
        new_piece = Piece(title=clean_form['title'],
                          date_of_composition=clean_form['composition_start_date'],
                          date_of_composition2=clean_form['composition_end_date'],
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
            composer_list = abstract_model_factory(clean_form['composer'], "Composer", clean,
                                                   birth_date=clean_form['composer_birth_date'],
                                                   death_date=clean_form['composer_death_date'])
            composer = composer_list[0]
            new_piece.composer = composer
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['collections']:
                collection_list = abstract_model_factory(clean_form['collections'], "Collection", clean, is_public=True, creator=request.user)
                for x in collection_list:
                    new_piece.collections.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['languages']:
                language_list = abstract_model_factory(clean_form['languages'], "Language", clean)
                for x in language_list:
                    new_piece.languages.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['genres']:
                genre_list = abstract_model_factory(clean_form['genres'], "Genre", clean)
                for x in genre_list:
                    new_piece.genres.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['locations']:
                location_list = abstract_model_factory(clean_form['locations'], "Location", clean)
                for x in location_list:
                    new_piece.locations.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['sources']:
                source_list = abstract_model_factory(clean_form['sources'], "Source", clean)
                for x in source_list:
                    new_piece.sources.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['tags']:
                tag_list = abstract_model_factory(clean_form['tags'], "Tag", clean)
                for x in tag_list:
                    new_piece.tags.add(x)
        except:
            clean.cleanup()
            raise
        try:
            if clean_form['instrument_voices']:
                instrument_list = abstract_model_factory(clean_form['instrument_voices'], "InstrumentVoice", clean)
                for x in instrument_list:
                    new_piece.instruments_voices.add(x)
        except:
            clean.cleanup()
            raise

        new_piece.save()
        try:
            handle_dynamic_file_table(request, new_piece, "piece", clean)
        except:
            clean.cleanup()
            raise
        try:
            handle_dynamic_file_table(request, new_piece, "mov", clean)
        except:
            clean.cleanup()
            raise

        new_piece.save()
        rebuild_suggester_dicts()
        return HttpResponseRedirect("http://localhost:8000/piece/{0}".format(new_piece.id))
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
import datetime
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
import pdb
import shutil

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer
from elvis.models.piece import Piece
from elvis.models import Composer
from elvis.forms import PieceForm

from elvis.views.views import handle_attachments, handle_movements, abstract_model_handler
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect


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
            return Response(status=status.HTTP_400_BAD_REQUEST)

        created = []

        clean_form = form.cleaned_data

        new_piece = Piece(title=clean_form['title'],
                          date_of_composition=clean_form['composition_start_date'],
                          date_of_composition2=clean_form['composition_end_date'],
                          number_of_voices=clean_form['number_of_voices'],
                          uploader=request.user,
                          created=datetime.datetime.now(),
                          updated=datetime.datetime.now())
        new_piece.save()
        created.append(new_piece)

        try:
            composer_list = abstract_model_handler(clean_form['composer'], "Composer",
                                                   birth_date=clean_form['composer_birth_date'],
                                                   death_date=clean_form['composer_death_date'])
            composer = composer_list[0]['model']
            if composer_list[0]['new']:
                created.append(composer)
        except:
            cleanup(created)
            raise

        try:
            if clean_form['collections']:
                collection_list = abstract_model_handler(clean_form['collections'], "Collection", is_public=True, creator=request.user)
                for x in collection_list:
                    new_piece.collections.add(x['model'])
                    if x['new']:
                        created.append(x['model'])
        except:
            cleanup(created)
            raise

        try:
            if clean_form['languages']:
                language_list = abstract_model_handler(clean_form['languages'], "Language")
                for x in language_list:
                    new_piece.languages.add(x['model'])
                    if x['new']:
                        created.append(x['model'])
        except:
            cleanup(created)
            raise
        try:
            attachments = handle_attachments(request, new_piece)
            created.extend(attachments)
        except:
            cleanup(created)
            raise
        try:
            movements = handle_movements(request, new_piece)
            created.extend(movements)
        except:
            cleanup(created)
            raise

        return HttpResponseRedirect("http://localhost:8000/new_piece/{0}".format(new_piece.id))


def cleanup(createdList):
    for item in createdList:
        item.delete()


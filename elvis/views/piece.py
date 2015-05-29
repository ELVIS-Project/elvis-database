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

    #TODO need to implement a check to see if the entire process was succesfull, and then delete everything unlinked if not.
    #TODO Piece may need to belong to multiple collections.

    def create(self, request, *args, **kwargs):
        if not request.user.is_active:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        form = PieceForm(request.POST)
        pdb.set_trace()
        if not form.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        created = []
        clean_form = form.cleaned_data

        # Check if we have composer, if not, create a new one with the given information.
        composer_dict = abstract_model_handler(clean_form['composer'], "Composer",
                                               birth_date=clean_form['composer_birth_date'],
                                               death_date=clean_form['composer_death_date'])
        composer = composer_dict['model']
        if composer_dict['new']:
            created.append(composer)



        piece = Piece(title=clean_form['title'],
                      composer=composer,
                      date_of_composition=clean_form['composition_start_date'],
                      date_of_composition2=clean_form['composition_end_date'],
                      number_of_voices=clean_form['number_of_voices'],

                      uploader=request.user,
                      created=datetime.datetime.now(),
                      updated=datetime.datetime.now())
        piece.save()
        created.append(piece)
        attachments = handle_attachments(request, piece)
        created.extend(attachments)
        movements = handle_movements(request, piece)
        created.extend(movements)
        pdb.set_trace()
        
        return HttpResponseRedirect("http://localhost:8000/piece/{0}".format(piece.id))


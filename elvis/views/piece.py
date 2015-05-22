from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
import datetime
import os
from elvis import settings
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.renderers import JSONRenderer
from django.http import JsonResponse
from rest_framework.response import Response
from django.http import HttpRequest
import pdb
import shutil

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.forms import PieceForm
from elvis.models.download import Download
from elvis.models.attachment import Attachment
from elvis.views.views import upload_files, handle_attachments
from zipfile import BadZipfile
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
        else:
            form = PieceForm(request.POST, request.FILES)

        if form.is_valid():
            clean_form = form.cleaned_data
            composer = handle_composer(clean_form['composer'])
            piece = Piece(title=clean_form['title'],
                          composer=composer,
                          uploader=request.user,
                          created=datetime.datetime.now(),
                          )
            piece.save()
            handle_attachments(request, piece)

            return HttpResponseRedirect("http://localhost:8000/piece/{0}".format(piece.id))
        else:
            return HttpResponseRedirect("http://localhost:8000/pieces/")

#TODO implement better behaviour for creating composers.
def handle_composer(composer):
    try:
        new_composer = Composer.objects.get(name=composer)
        return new_composer
    except:
        new_composer = Composer(name=composer, created=datetime.date)
        new_composer.save()
        return new_composer
    pass


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

from elvis.exceptions import NoFilesError
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer
from elvis.models.piece import Piece
from elvis.forms import PieceForm

from elvis.views.views import handle_attachments, handle_composer
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

        form = PieceForm(request.POST, request.FILES)

        if not form.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        clean_form = form.cleaned_data

        composer = handle_composer(clean_form)
        piece = Piece(title=clean_form['title'],
                      composer=composer,
                      uploader=request.user,
                      created=datetime.datetime.now(),
                      updated=datetime.datetime.now()
                      )
        piece.save()

        try:
            handle_attachments(request, piece)
        except NoFilesError:
            piece.delete()
            return render(request, "415.html")

        return HttpResponseRedirect("http://localhost:8000/piece/{0}".format(piece.id))


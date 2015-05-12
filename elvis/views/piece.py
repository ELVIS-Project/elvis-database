from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework import generics
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
import pdb;

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.piece import PieceSerializer
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.forms import PieceForm
from elvis.models.download import Download
from elvis.models.attachment import Attachment

from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect


class PieceListHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_list.html"


class PieceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_detail.html"


class PieceCreateHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/piece_create.html"


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
        form = PieceForm(request.POST, request.FILES)
        if form.is_valid():
            clean_form = form.cleaned_data
            piece = Piece(title=clean_form['title'],
                          composer=Composer.objects.get(name__icontains="{0}".format(clean_form['composer']))
                          )
            piece.save()

            return HttpResponseRedirect("http://localhost:8000/piece/{0}".format(piece.id))
        else:
            return HttpResponseRedirect("http://localhost:8000/pieces/")

    def handle(self, composer):
        return


class PieceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceDetailHTMLRenderer)
    queryset = Piece.objects.all()


class PieceCreate(generics.CreateAPIView):
    model = Piece
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PieceSerializer
    renderer_classes = (JSONRenderer, PieceCreateHTMLRenderer)
    queryset = Piece.objects.all()

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


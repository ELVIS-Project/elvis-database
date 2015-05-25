# AP: NO LONGER USED. Keeping it here so I can reference the work already done for uploads.

# LM: TODO lots of cleaning up; make modular methods
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse

from django.template import RequestContext
from django.shortcuts import render_to_response

import os, json

from time import sleep

import datetime

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.create import CreatePieceSerializer
from elvis.helpers.solrsearch import SolrSearch
from elvis.settings import ELVIS_EXTENSIONS
from elvis.forms import PieceForm

class CreatePieceHTMLRenderer(CustomHTMLRenderer):
    template_name = "create/create_piece.html"

class CreatePiece(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CreatePieceSerializer
    renderer_classes = (JSONRenderer, CreatePieceHTMLRenderer)

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        return create_piece(request)

# TODO: Error handling for tag list 
# TODO: Error handling for corpus - must exist
# TODO: If corpus does not exist, should raise error
def create_piece(request):
    form = PieceForm(request.POST, request.FILES)
    if form.is_valid():
        clean_form = form.cleaned_data
        uploader = request.user
        # Handle tags
        tags = tag_handler(clean_form['tags'])
        # Handle composer and corpus
        composer = composer_handler(clean_form.get('composer'))
        corpus = object_handler(Corpus, clean_form.get('corpus'))
        date = date_handler(clean_form.get('date_of_composition'))
        
        # Create piece
        piece = Piece(title=clean_form['title'],
                        composer=composer,
                        corpus=corpus,
                        date_of_composition=date,
                        number_of_voices=clean_form.get('number_of_voices'),
                        comment=clean_form.get('comment'),
                        uploader=uploader )
        piece.save()

        attachments = []
        # Create movements associated with piece (if any)
        # Also return attachment associated with piece if possible
        attachments.extend(movement_files_handler(request.POST, request.FILES, piece))

        # Add tags to piece
        for tag in tags:
            piece.tags.add(tag)
        piece.save()

        # Add attachments to piece
        for attachment in attachments:
            piece.attachments.add(attachment)
        piece.save()

        data = {
                'model_type': 'piece',
                'model_pk': piece.id,
                'model_url': request.build_absolute_uri(os.path.join('/piece/', piece.id))
        }

        return Response(data=data, status=status.HTTP_201_CREATED)

    return render(request, 'forms/piece.html', {'form':form})

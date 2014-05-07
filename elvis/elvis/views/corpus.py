from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.corpus import CorpusSerializer
from elvis.models.corpus import Corpus


class CorpusListHTMLRenderer(CustomHTMLRenderer):
    template_name = "corpus/corpus_list.html"


class CorpusDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "corpus/corpus_detail.html"


class CorpusList(generics.ListCreateAPIView):
    model = Corpus
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CorpusSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, CorpusListHTMLRenderer)
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100



class CorpusDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Corpus
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CorpusSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, CorpusDetailHTMLRenderer)

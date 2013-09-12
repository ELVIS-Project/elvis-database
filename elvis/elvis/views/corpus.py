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


class CorpusDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Corpus
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CorpusSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, CorpusDetailHTMLRenderer)

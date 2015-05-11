from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.source import SourceSerializer
from elvis.models.source import Source

class SourceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "source/source_detail.html"

class SourceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Source
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SourceSerializer
    renderer_classes = (JSONRenderer, SourceDetailHTMLRenderer)

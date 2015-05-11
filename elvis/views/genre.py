from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.genre import GenreSerializer
from elvis.models.genre import Genre

class GenreDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "genre/genre_detail.html"

class GenreDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Genre
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = GenreSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, GenreDetailHTMLRenderer)

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.composer import ComposerSerializer
from elvis.models.composer import Composer

class ComposerListHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_list.html"


class ComposerDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_detail.html"


class ComposerList(generics.ListCreateAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ComposerListHTMLRenderer)


class ComposerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ComposerDetailHTMLRenderer)

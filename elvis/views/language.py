from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.language import LanguageSerializer
from elvis.models.language import Language

class LanguageDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "language/language_detail.html"

class LanguageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Language
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = LanguageSerializer
    renderer_classes = (JSONRenderer, LanguageDetailHTMLRenderer)

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.composer import ComposerSerializer, ComposerListSerializer
from elvis.models.composer import Composer


class ComposerListHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_list.html"


class ComposerDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_detail.html"


class ComposerList(generics.ListCreateAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerListSerializer
    renderer_classes = (JSONRenderer, ComposerListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 20
    queryset = Composer.objects.all()

    def get_queryset(self):
        query = self.request.GET.get('q', None)
        if query:
            return self.queryset.filter(name=query)
        else:
            return self.queryset

class ComposerDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Composer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ComposerSerializer
    renderer_classes = (JSONRenderer, ComposerDetailHTMLRenderer)
    queryset = Composer.objects.all()

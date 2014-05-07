from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.tag import TagSerializer
from elvis.models.tag import Tag


class TagListHTMLRenderer(CustomHTMLRenderer):
    template_name = "tag/tag_list.html"


class TagDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "tag/tag_detail.html"


class TagList(generics.ListCreateAPIView):
    model = Tag
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, TagListHTMLRenderer)
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Tag
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, TagDetailHTMLRenderer)

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.tag import TagSerializer
from elvis.models.tag import Tag
#from elvis.models.tag_hierarchy import TagHierarchy

class TagListHTMLRenderer(CustomHTMLRenderer):
    template_name = "tag/tag_tree.html"


class TagDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "tag/tag_detail.html"


class TagList(generics.ListCreateAPIView):
    model = Tag
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    renderer_classes = (JSONRenderer, TagListHTMLRenderer)
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Tag.objects.all()


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Tag
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer
    renderer_classes = (JSONRenderer, TagDetailHTMLRenderer)
    queryset = Tag.objects.all()
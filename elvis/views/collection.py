from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.collection import CollectionSerializer
from elvis.models.collection import Collection


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


class CollectionList(generics.ListCreateAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionSerializer
    renderer_classes = (JSONRenderer, CollectionListHTMLRenderer)
    paginate_by = 10
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Collection.objects.all()


class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionSerializer
    renderer_classes = (JSONRenderer, CollectionDetailHTMLRenderer)
    queryset = Collection.objects.all()

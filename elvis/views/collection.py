from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from elvis.models import Download
from elvis.serializers.download import DownloadSerializer
from django.core.exceptions import ObjectDoesNotExist

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.collection import CollectionSerializer, CollectionListSerializer
from elvis.models.collection import Collection


class CollectionListHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_list.html"


class CollectionDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_detail.html"


class CollectionCurrentHTMLRenderer(CustomHTMLRenderer):
    template_name = "collection/collection_current.html"


class CollectionList(generics.ListCreateAPIView):
    model = Collection
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = CollectionListSerializer
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


class CollectionCurrent(generics.RetrieveUpdateDestroyAPIView):
    model = Download
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DownloadSerializer
    renderer_classes = (JSONRenderer, CollectionCurrentHTMLRenderer)
    queryset = Download.objects.all()

    def get_object(self):
        user = self.request.user
        try:
            obj = Download.objects.filter(user=user).latest("created")
            return obj
        except ObjectDoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        if User.is_authenticated(request.user):
            return self.retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
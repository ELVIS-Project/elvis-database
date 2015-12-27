from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import MovementFullSerializer, MovementListSerializer
from elvis.models.movement import Movement


class MovementListHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_list.html"


class MovementDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_detail.html"


class MovementList(generics.ListCreateAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementListSerializer
    renderer_classes = (JSONRenderer, MovementListHTMLRenderer)
    paginate_by = 20
    paginate_by_param = 'page_size'
    max_paginate_by = 100
    queryset = Movement.objects.all()


class MovementDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementFullSerializer
    renderer_classes = (JSONRenderer, MovementDetailHTMLRenderer)
    queryset = Movement.objects.all()

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.movement import MovementSerializer
from elvis.models.movement import Movement


class MovementListHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_list.html"


class MovementDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_detail.html"


class MovementList(generics.ListCreateAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, MovementListHTMLRenderer)


class MovementDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Movement
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = MovementSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, MovementDetailHTMLRenderer)

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers import MovementFullSerializer, MovementListSerializer
from elvis.models.movement import Movement
from elvis.views.common import ElvisListCreateView, ElvisDetailView


class MovementListHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_list.html"


class MovementDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "movement/movement_detail.html"


class MovementList(ElvisListCreateView):
    model = Movement
    serializer_class = MovementListSerializer
    renderer_classes = (MovementListHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)


class MovementDetail(ElvisDetailView):
    model = Movement
    serializer_class = MovementFullSerializer
    renderer_classes = (MovementDetailHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

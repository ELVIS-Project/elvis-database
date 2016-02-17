from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.serializers import ComposerFullSerializer, ComposerListSerializer
from elvis.models.composer import Composer
from elvis.views.common import ElvisListCreateView, ElvisDetailView


class ComposerListHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_list.html"


class ComposerDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "composer/composer_detail.html"


class ComposerList(ElvisListCreateView):
    model = Composer
    serializer_class = ComposerListSerializer
    renderer_classes = (ComposerListHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)


class ComposerDetail(ElvisDetailView):
    model = Composer
    serializer_class = ComposerFullSerializer
    renderer_classes = (ComposerDetailHTMLRenderer, JSONRenderer, BrowsableAPIRenderer)

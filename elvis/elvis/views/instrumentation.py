from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.instrumentation import InstrumentVoiceSerializer
from elvis.models.instrumentation import InstrumentVoice

class InstrumentVoiceDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "instrumentation/instrumentation_detail.html"

class InstrumentVoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    model = InstrumentVoice
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = InstrumentVoiceSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, InstrumentVoiceDetailHTMLRenderer)

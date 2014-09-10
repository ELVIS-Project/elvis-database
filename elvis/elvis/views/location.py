from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.location import LocationSerializer
from elvis.models.location import Location

class LocationDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "location/location_detail.html"

class LocationDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = LocationSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, LocationDetailHTMLRenderer)

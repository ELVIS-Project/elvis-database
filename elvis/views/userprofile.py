from elvis.models.userprofile import UserProfile
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer

from elvis.serializers.userprofile import UserProfileSerializer
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer


class UserProfileListHTMLRenderer(CustomHTMLRenderer):
    template_name = "userprofile/userprofile_list.html"


class UserProfileDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "userprofile/userprofile_detail.html"


class UserProfileList(generics.ListCreateAPIView):
    model = UserProfile
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserProfileSerializer
    renderer_classes = (JSONRenderer, UserProfileListHTMLRenderer)


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    model = UserProfile
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserProfileSerializer
    renderer_classes = (JSONRenderer, UserProfileDetailHTMLRenderer)
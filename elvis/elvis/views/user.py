from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.serializers.user import UserSerializer
from elvis.renderers.custom_html_renderer import CustomHTMLRenderer


class UserListHTMLRenderer(CustomHTMLRenderer):
    template_name = "user/user_list.html"


class UserDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "user/user_detail.html"


class UserList(generics.ListCreateAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, UserListHTMLRenderer)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    model = User
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, UserDetailHTMLRenderer)

from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.project import ProjectSerializer
from elvis.models.project import Project


class ProjectListHTMLRenderer(CustomHTMLRenderer):
    template_name = "project/project_list.html"


class ProjectDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "piece/project_detail.html"


class ProjectList(generics.ListCreateAPIView):
    model = Project
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ProjectSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ProjectListHTMLRenderer)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Project
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = ProjectSerializer
    renderer_classes = (JSONRenderer, JSONPRenderer, ProjectDetailHTMLRenderer)

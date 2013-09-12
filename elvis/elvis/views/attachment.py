from rest_framework import generics
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer, JSONPRenderer

from elvis.renderers.custom_html_renderer import CustomHTMLRenderer
from elvis.serializers.attachment import AttachmentSerializer
from elvis.models.attachment import Attachment


'''
class AttachmentListHTMLRenderer(CustomHTMLRenderer):
    template_name = "attachment/attachment_list.html"


class AttachmentDetailHTMLRenderer(CustomHTMLRenderer):
    template_name = "attachment/attachment_detail.html"
'''


class AttachmentList(generics.ListCreateAPIView):
    model = Attachment
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AttachmentSerializer
    #renderer_classes = (JSONRenderer, JSONPRenderer, AttachmentListHTMLRenderer)


class AttachmentDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Attachment
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = AttachmentSerializer
    #renderer_classes = (JSONRenderer, JSONPRenderer, AttachmentDetailHTMLRenderer)

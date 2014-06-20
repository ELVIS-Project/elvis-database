from rest_framework import serializers
from elvis.models.attachment import Attachment

from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
import mimetypes

import os
from django.conf import settings

class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    attachment = serializers.SerializerMethodField("retrieve_attachment")
    file_name = serializers.Field()
    attachment_path = serializers.Field()
    
    class Meta:
        model = Attachment
        fields = ("file_name", "id", "url", "old_id", "created", "updated", "description", "uploader", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url

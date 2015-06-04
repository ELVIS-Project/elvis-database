from rest_framework import serializers
from elvis.models.attachment import Attachment
import os
from django.conf import settings


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    attachment = serializers.SerializerMethodField("retrieve_attachment")
    source = serializers.CharField()
    file_name = serializers.Field()
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)

    class Meta:
        model = Attachment
        fields = ("file_name", "id", 'source', "url", "old_id", "created", "updated", "description", "uploader", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url

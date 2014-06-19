from rest_framework import serializers
from elvis.models.attachment import Attachment


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    file_name = serializers.Field()
    class Meta:
        model = Attachment
        fields = ("file_name", "id", "url", "old_id", "created", "updated", "description", "uploader")

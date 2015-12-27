from rest_framework import serializers
from elvis.models.attachment import Attachment


class AttachmentMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "extension", "url")


class AttachmentFullSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Attachment
        fields = ("file_name", "extension", "id", 'source', "url", "created", "updated", "uploader", "attachment")
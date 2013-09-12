from rest_framework import serializers
from elvis.models.attachment import Attachment


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment

from rest_framework import serializers
from elvis.models.download import Download
from elvis.models.attachment import Attachment
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from django.contrib.auth.models import User

class UserDownloadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username')

class AttachmentComposerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', 'name', 'id')

class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    class Meta:
        model = Piece
        fields = ('url', 'title', 'date_of_composition',  'date_of_composition2', 'composer', 'id')

class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    class Meta:
        model = Movement
        fields = ('url', 'title', 'date_of_composition', 'date_of_composition2', 'composer', 'id')

class UserAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    pieces = AttachmentPieceSerializer()
    movements = AttachmentMovementSerializer()
    file_name = serializers.Field()
    attachment_path = serializers.Field()
    class Meta:
        model = Attachment
        fields = ('url', 'pieces', 'movements', 'attachment', 'file_name', 'id')


class DownloadSerializer(serializers.ModelSerializer):
    user = UserDownloadSerializer()
    attachments = UserAttachmentSerializer()
    class Meta:
        model = Download

class DownloadingSerializer(serializers.Serializer):
    class Meta:
        pass
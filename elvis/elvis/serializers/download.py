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
        fields = ('url', 'name')

class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    class Meta:
        model = Piece
        fields = ('url', 'title', 'composer')

class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    class Meta:
        model = Movement
        fields = ('url', 'title', 'composer')

class UserAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    pieces = AttachmentPieceSerializer()
    movements = AttachmentMovementSerializer()
    class Meta:
        model = Attachment
        fields = ('url', 'pieces', 'movements', 'attachment')


class DownloadSerializer(serializers.ModelSerializer):
    user = UserDownloadSerializer()
    attachments = UserAttachmentSerializer()
    class Meta:
        model = Download

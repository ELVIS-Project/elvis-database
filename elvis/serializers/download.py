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
    date_of_composition = serializers.DateField(format=None)
    date_of_composition2 = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'title', 'date_of_composition',  'date_of_composition2', 'composer', 'id')


class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    date_of_composition = serializers.DateField(format=None)
    date_of_composition2 = serializers.DateField(format=None)

    class Meta:
        model = Movement
        fields = ('url', 'title', 'date_of_composition', 'date_of_composition2', 'composer', 'id')


class UserAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    pieces = AttachmentPieceSerializer(many=True)
    movements = AttachmentMovementSerializer(many=True)
    file_name = serializers.ReadOnlyField()
    attachment_path = serializers.ReadOnlyField()

    class Meta:
        model = Attachment
        fields = ('url', 'pieces', 'movements', 'attachment', 'attachment_path', 'file_name', 'id')


class DownloadPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ('title', 'url')


class DownloadMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movement
        fields = ('title', 'url',)


class DownloadSerializer(serializers.ModelSerializer):
    user = UserDownloadSerializer()
    collection_pieces = DownloadPieceSerializer(many=True)
    collection_movements = DownloadMovementSerializer(many=True)
    attachments = UserAttachmentSerializer(many=True)
    created = serializers.DateField(format=None)

    class Meta:
        model = Download


class DownloadingSerializer(serializers.Serializer):
    class Meta:
        pass
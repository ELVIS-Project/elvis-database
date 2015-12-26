from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer


class AttachmentComposerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', 'name', 'id')


class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    composition_start_date = serializers.DateField(format=None)
    composition_end_date = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'title', 'composition_start_date',  'composition_end_date', 'composer', 'id')


class DownloadMovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    piece = AttachmentPieceSerializer()
    composition_start_date = serializers.DateField(format=None)
    composition_end_date = serializers.DateField(format=None)

    class Meta:
        model = Movement
        fields = ('url', 'title', 'composition_start_date', 'composition_end_date', 'composer', 'id', 'piece')


class DownloadPieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = AttachmentComposerSerializer()
    composition_start_date = serializers.DateField(format=None)
    composition_end_date = serializers.DateField(format=None)
    class Meta:
        model = Piece
        fields = ('title', 'id', 'composer', 'url', 'movement_count', 'composition_start_date', 'composition_end_date',)


class DownloadingSerializer(serializers.Serializer):
    class Meta:
        pass
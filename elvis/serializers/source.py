from rest_framework import serializers
from elvis.models.source import Source
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer


class SourceComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")


class SourceMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class SourcePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = SourceMovementSerializer(many=True)
    composer = SourceComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    composition_start_date = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "composition_start_date", "composer")


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    pieces = SourcePieceSerializer(many=True)

    class Meta:
        model = Source
        fields = ('pieces', 'comment', 'name')

from rest_framework import serializers
from elvis.models.source import Source
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class SourceComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Composer
        fields = ("url", "name", "item_id")

class SourceMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class SourcePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = SourceMovementSerializer()
    composer = SourceComposerSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition", "composer")


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    pieces = SourcePieceSerializer()

    class Meta:
        model = Source
        fields = ('pieces', 'comment', 'name')

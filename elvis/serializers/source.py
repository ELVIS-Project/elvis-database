from rest_framework import serializers
from elvis.models.source import Source
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class SourceComposerSerializer(serializers.HyperlinkedModelSerializer):
    #item_id = serializers.Field()

    class Meta:
        model = Composer
        fields = ("url", "name")

class SourceMovementSerializer(serializers.HyperlinkedModelSerializer):
    #item_id = serializers.Field()

    class Meta:
        model = Movement
        fields = ('url', 'title')


class SourcePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = SourceMovementSerializer(many=True)
    composer = SourceComposerSerializer()
    #item_id = serializers.Field()

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "date_of_composition", "composer")


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    pieces = SourcePieceSerializer(many=True)

    class Meta:
        model = Source
        fields = ('pieces', 'comment', 'name')

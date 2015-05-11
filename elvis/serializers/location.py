from rest_framework import serializers
from elvis.models.location import Location
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class LocationComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Composer
        fields = ("url", "name", "item_id")

class LocationMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class LocationPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = LocationMovementSerializer()
    composer = LocationComposerSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition", "composer")


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    pieces = LocationPieceSerializer()

    class Meta:
        model = Location
        fields = ('pieces', 'comment', 'name')

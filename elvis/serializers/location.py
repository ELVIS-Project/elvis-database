from rest_framework import serializers
from elvis.models.location import Location
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer


class LocationComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")


class LocationMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class LocationPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = LocationMovementSerializer(many=True)
    composer = LocationComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    composition_start_date = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "composition_start_date", "composer")


class LocationSerializer(serializers.HyperlinkedModelSerializer):
    pieces = LocationPieceSerializer(many=True)

    class Meta:
        model = Location
        fields = ('pieces', 'comment', 'name')

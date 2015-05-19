from rest_framework import serializers
from elvis.models.tag import Tag
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class TagComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")

class TagMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class TagPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = TagMovementSerializer(many=True)
    composer = TagComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "date_of_composition", "composer")


class TagSerializer(serializers.HyperlinkedModelSerializer):
    pieces = TagPieceSerializer(many=True)

    class Meta:
        model = Tag
        fields = ('pieces', 'description', 'name')

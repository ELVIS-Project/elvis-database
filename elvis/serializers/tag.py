from rest_framework import serializers
from elvis.models.tag import Tag
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class TagComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Composer
        fields = ("url", "name", "item_id")

class TagMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class TagPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = TagMovementSerializer()
    composer = TagComposerSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition", "composer")


class TagSerializer(serializers.HyperlinkedModelSerializer):
    pieces = TagPieceSerializer()

    class Meta:
        model = Tag
        fields = ('pieces', 'description', 'name')

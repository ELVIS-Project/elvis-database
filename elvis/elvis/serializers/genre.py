from rest_framework import serializers
from elvis.models.genre import Genre
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class GenreComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Composer
        fields = ("url", "name", "item_id")

class GenreMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class GenrePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = GenreMovementSerializer()
    composer = GenreComposerSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition", "composer")


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    pieces = GenrePieceSerializer()

    class Meta:
        model = Genre
        fields = ('pieces', 'comment', 'name')

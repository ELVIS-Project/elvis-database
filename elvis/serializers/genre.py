from rest_framework import serializers
from elvis.models.genre import Genre
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer


class GenreComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")


class GenreMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class GenrePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = GenreMovementSerializer(many=True)
    composer = GenreComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    date_of_composition = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "date_of_composition", "composer")


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    pieces = GenrePieceSerializer(many=True)

    class Meta:
        model = Genre
        fields = ('pieces', 'comment', 'name')

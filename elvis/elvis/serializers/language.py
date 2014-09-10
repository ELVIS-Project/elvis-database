from rest_framework import serializers
from elvis.models.language import Language
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class LanguageComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Composer
        fields = ("url", "name", "item_id")

class LanguageMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")

    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class LanguagePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = LanguageMovementSerializer()
    composer = LanguageComposerSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition", "composer")


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    pieces = LanguagePieceSerializer()

    class Meta:
        model = Language
        fields = ('pieces', 'comment', 'name')

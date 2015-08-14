from rest_framework import serializers
from elvis.models.language import Language
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer


class LanguageComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")


class LanguageMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class LanguagePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = LanguageMovementSerializer(many=True)
    composer = LanguageComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    composition_start_date = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "composition_start_date", "composer")


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    pieces = LanguagePieceSerializer(many=True)

    class Meta:
        model = Language
        fields = ('pieces', 'comment', 'name')

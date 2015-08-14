from rest_framework import serializers
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer


class InstrumentVoiceComposerSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Composer
        fields = ("url", 'item_id', "name")


class InstrumentVoiceMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class InstrumentVoicePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = InstrumentVoiceMovementSerializer(many=True)
    composer = InstrumentVoiceComposerSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    composition_start_date = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "composition_start_date", "composer")


class InstrumentVoiceSerializer(serializers.HyperlinkedModelSerializer):
    pieces = InstrumentVoicePieceSerializer(many=True)

    class Meta:
        model = InstrumentVoice
        fields = ('pieces', 'comment', 'name')

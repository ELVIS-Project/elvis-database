from rest_framework import serializers
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.movement import Movement
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.serializers.piece import PieceSerializer

class InstrumentVoiceComposerSerializer(serializers.HyperlinkedModelSerializer):
    #item_id = serializers.Field()

    class Meta:
        model = Composer
        fields = ("url", "name")

class InstrumentVoiceMovementSerializer(serializers.HyperlinkedModelSerializer):
    #item_id = serializers.Field()

    class Meta:
        model = Movement
        fields = ('url', 'title')


class InstrumentVoicePieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = InstrumentVoiceMovementSerializer(many=True)
    composer = InstrumentVoiceComposerSerializer()
    #item_id = serializers.Field()

    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "date_of_composition", "composer")


class InstrumentVoiceSerializer(serializers.HyperlinkedModelSerializer):
    pieces = InstrumentVoicePieceSerializer(many=True)

    class Meta:
        model = InstrumentVoice
        fields = ('pieces', 'comment', 'name')

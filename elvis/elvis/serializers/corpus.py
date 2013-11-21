from rest_framework import serializers
from elvis.serializers.user import UserSerializer
from elvis.models.corpus import Corpus
from elvis.models.piece import Piece
from elvis.models.movement import Movement


class PieceCorpusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece


class MovementCorpusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movement


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer()
    pieces = PieceCorpusSerializer()
    movements = MovementCorpusSerializer()

    class Meta:
        model = Corpus

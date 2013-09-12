from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.serializers.composer import ComposerSerializer


class PieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerSerializer()

    class Meta:
        model = Piece

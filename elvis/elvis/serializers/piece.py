from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.serializers.composer import ComposerSerializer
from elvis.serializers.user import UserSerializer


class PieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerSerializer()
    uploader = UserSerializer()

    class Meta:
        model = Piece

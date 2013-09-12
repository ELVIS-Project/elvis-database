from rest_framework import serializers
from elvis.models.tag import Tag
from elvis.serializers.piece import PieceSerializer


class TagSerializer(serializers.HyperlinkedModelSerializer):
    pieces = PieceSerializer()

    class Meta:
        model = Tag

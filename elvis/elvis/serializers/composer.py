from rest_framework import serializers
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement

class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece


class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movement


class ComposerSerializer(serializers.HyperlinkedModelSerializer):
    pieces = ComposerPieceSerializer()
    movements = ComposerMovementSerializer()
    class Meta:
        model = Composer
        fields = ("url",
                  "id",
                  "old_id",
                  "name",
                  "birth_date",
                  "death_date",
                  "picture",
                  "pieces",
                  "movements",
                  "number_of_queries",
                  "created",
                  "updated")

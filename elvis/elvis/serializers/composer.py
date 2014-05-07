from rest_framework import serializers
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement


class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field("pk")
    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = ComposerMovementSerializer()
    item_id = serializers.Field("pk")
    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id")


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
                  "created",
                  "updated")

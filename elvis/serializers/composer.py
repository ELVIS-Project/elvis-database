from rest_framework import serializers
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from django.conf import settings
import os


class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    movement_count = serializers.ReadOnlyField(source='movements.count')
    item_id = serializers.ReadOnlyField(source='pk')
    date_of_composition = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movement_count', "date_of_composition")


class ComposerHistorySerializer(serializers.HyperlinkedModelSerializer):
    history_user_id = serializers.ReadOnlyField()
    updated = serializers.DateTimeField()

    class Meta:
        model = Composer
        fields = ('history_user_id', 'updated')


class ComposerSerializer(serializers.HyperlinkedModelSerializer):
    pieces = ComposerPieceSerializer(many=True)
    free_movements = ComposerMovementSerializer(many=True)
    free_movements_count = serializers.ReadOnlyField()
    item_id = serializers.ReadOnlyField(source='pk')
    birth_date = serializers.DateField(format=None)
    death_date = serializers.DateField(format=None)
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    history = ComposerHistorySerializer(many=True)

    class Meta:
        model = Composer
        fields = ("url",
                  "id",
                  "item_id",
                  "old_id",
                  "name",
                  "birth_date",
                  "death_date",
                  "pieces",
                  "free_movements",
                  "free_movements_count",
                  "created",
                  "updated",
                  "history")



class ComposerListSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')
    birth_date = serializers.DateField(format=None)
    death_date = serializers.DateField(format=None)
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    piece_count = serializers.IntegerField()
    movement_count = serializers.IntegerField()

    class Meta:
        model = Composer
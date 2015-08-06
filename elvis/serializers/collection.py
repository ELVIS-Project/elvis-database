from rest_framework import serializers
from elvis.models.collection import Collection
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from django.contrib.auth.models import User


class ComposerCollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ("url", "name")


class PieceCollectionSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerCollectionSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    date_of_composition = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ("url", "item_id", "title", "composer", "movement_count", "date_of_composition")


class PieceMovementCollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ("url", "title", "pk")


class MovementCollectionSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerCollectionSerializer()
    piece = PieceMovementCollectionSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    date_of_composition = serializers.DateField(format=None)

    class Meta:
        model = Movement
        fields = ("url", "item_id", "title", "composer", "date_of_composition", "piece")


class UserCollectionSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("url", "full_name", "username")

    def get_full_name(self, obj):
        if not obj.last_name:
            return u"{0}".format(obj.username)
        else:
            return u"{0} {1}".format(obj.first_name, obj.last_name)


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserCollectionSerializer()
    pieces = PieceCollectionSerializer(many=True)
    item_id = serializers.ReadOnlyField(source='pk')
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    movements = MovementCollectionSerializer(many=True)
    movement_count = serializers.IntegerField()

    class Meta:
        model = Collection


class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserCollectionSerializer()
    item_id = serializers.ReadOnlyField(source='pk')
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    piece_count = serializers.IntegerField()
    movement_count = serializers.IntegerField()

    class Meta:
        model = Collection
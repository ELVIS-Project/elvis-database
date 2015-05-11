from rest_framework import serializers
from elvis.serializers.user import UserSerializer
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
    #item_id = serializers.ReadOnlyField('pk')
    number_of_movements = serializers.Field(source="number_of_movements")
    class Meta:
        model = Piece
        fields = ("url", "title", "composer", "number_of_movements", "date_of_composition",)

class PieceMovementCollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ("url", "title")

class MovementCollectionSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerCollectionSerializer()
    piece = PieceMovementCollectionSerializer()
    #item_id = serializers.ReadOnlyField('pk')
    class Meta:
        model = Movement
        fields = ("url", "title", "composer", "date_of_composition", "piece")

class UserCollectionSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    class Meta:
        model = User
        fields = ("url", "full_name")

    def get_full_name(self, obj):
        if not obj.last_name:
            return u"{0}".format(obj.username)
        else:
            return u"{0} {1}".format(obj.first_name, obj.last_name)


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserCollectionSerializer()
    pieces = PieceCollectionSerializer(many=True)
    movements = MovementCollectionSerializer(many=True)
    #item_id = serializers.ReadOnlyField('pk')

    class Meta:
        model = Collection

from rest_framework import serializers
from django.contrib.auth.models import User
from elvis.models.piece import Piece
from elvis.models.movement import Movement


class UserPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ('url', 'title')


class UserMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movement
        fields = ('url', 'title')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField()
    pieces = UserPieceSerializer(many=True)
    movements = UserMovementSerializer(many=True)

    class Meta:
        model = User

    def get_full_name(self, obj):
        if not obj.last_name:
            return "{0}".format(obj.username)
        else:
            return "{0} {1}".format(obj.first_name, obj.last_name)

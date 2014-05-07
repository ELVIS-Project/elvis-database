from rest_framework import serializers
from elvis.serializers.user import UserSerializer
from elvis.models.corpus import Corpus
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from django.contrib.auth.models import User


class ComposerCorpusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ("url", "name")


class PieceCorpusSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerCorpusSerializer()
    number_of_movements = serializers.Field(source="number_of_movements")
    class Meta:
        model = Piece
        fields = ("url", "title", "composer", "number_of_movements")


class MovementCorpusSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerCorpusSerializer()
    class Meta:
        model = Movement
        fields = ("url", "title", "composer", "piece")


class UserCorpusSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    class Meta:
        model = User
        fields = ("url", "full_name")


    def get_full_name(self, obj):
        if not obj.last_name:
            return u"{0}".format(obj.username)
        else:
            return u"{0} {1}".format(obj.first_name, obj.last_name)


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserCorpusSerializer()
    pieces = PieceCorpusSerializer()
    movements = MovementCorpusSerializer()

    class Meta:
        model = Corpus

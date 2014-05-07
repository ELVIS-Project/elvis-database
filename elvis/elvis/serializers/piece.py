from rest_framework import serializers
from elvis.models.piece import Piece
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.attachment import Attachment
from elvis.models.corpus import Corpus
from elvis.models.movement import Movement
from django.contrib.auth.models import User


class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', "name")

class TagPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ("url", "name")

class AttachmentPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("attachment","description")

class CorpusPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corpus
        fields = ("url", "title")

class UserPieceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', "last_name")

class MovementPieceSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field('pk')
    class Meta:
        model = Movement
        fields = ('url', 'title', 'item_id')

class PieceSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerPieceSerializer()
    tags = TagPieceSerializer()
    attachments = AttachmentPieceSerializer()
    corpus = CorpusPieceSerializer()
    uploader = UserPieceSerializer()
    movements = MovementPieceSerializer()
    item_id = serializers.Field("pk")

    class Meta:
        model = Piece

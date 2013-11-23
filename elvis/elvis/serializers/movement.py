from rest_framework import serializers
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.attachment import Attachment
from elvis.models.corpus import Corpus
from django.contrib.auth.models import User


class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', "name")

class TagMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ("url", "name")

class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("attachment","description")

class CorpusMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corpus
        fields = ("url", "title")

class UserMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', "last_name")


class MovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMovementSerializer()
    tags = TagMovementSerializer()
    attachments = AttachmentMovementSerializer()
    corpus = CorpusMovementSerializer()
    uploader = UserMovementSerializer()
    item_id = serializers.Field("pk")
    class Meta:
        model = Movement

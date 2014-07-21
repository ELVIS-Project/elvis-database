from rest_framework import serializers
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.attachment import Attachment
from elvis.models.corpus import Corpus
from elvis.models.piece import Piece
from django.contrib.auth.models import User

import os
from django.conf import settings

class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('url', "name")

class TagMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ("url", "name")

class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    # LM: Must add this to serializers explicitly, otherwise will raise KeyError
    file_name = serializers.Field()
    attachment = serializers.SerializerMethodField("retrieve_attachment")

    class Meta:
        model = Attachment
        fields = ("file_name", "id", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url

class CorpusMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corpus
        fields = ("url", "title")

class UserMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', "last_name")

class PieceMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ("url", "title")


class MovementSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMovementSerializer()
    tags = TagMovementSerializer()
    attachments = AttachmentMovementSerializer()
    corpus = CorpusMovementSerializer()
    uploader = UserMovementSerializer()
    piece = PieceMovementSerializer()
    item_id = serializers.Field("pk")
    class Meta:
        model = Movement

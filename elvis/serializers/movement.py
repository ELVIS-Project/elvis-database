from rest_framework import serializers
from elvis.models.movement import Movement
from elvis.models.composer import Composer
from elvis.models.tag import Tag
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.location import Location
from elvis.models.source import Source
from elvis.models.attachment import Attachment
from elvis.models.collection import Collection
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

class GenreMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ("name", )

class InstrumentVoiceMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = InstrumentVoice
        fields = ("name", )

class LanguageMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = ("name", )

class LocationMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields =("name", )

class SourceMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Source
        fields = ("name", )

class AttachmentMovementSerializer(serializers.HyperlinkedModelSerializer):
    # LM: Must add this to serializers explicitly, otherwise will raise KeyError
    file_name = serializers.Field()
    attachment = serializers.SerializerMethodField("retrieve_attachment")

    class Meta:
        model = Attachment
        fields = ("file_name", "id", "attachment")

    def retrieve_attachment(self, obj):
        request = self.context.get('request', None)
        if not request.user.is_authenticated():
            return ""
        path = os.path.relpath(obj.attachment.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url


class CollectionMovementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
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
    genres = GenreMovementSerializer()
    instruments_voices = InstrumentVoiceMovementSerializer()
    languages = LanguageMovementSerializer()
    locations = LocationMovementSerializer()
    sources = SourceMovementSerializer()
    attachments = AttachmentMovementSerializer()
    collections = CollectionMovementSerializer()
    uploader = UserMovementSerializer()
    piece = PieceMovementSerializer()
    item_id = serializers.Field("pk")
    class Meta:
        model = Movement

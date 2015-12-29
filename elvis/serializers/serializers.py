from rest_framework import serializers
from django.contrib.auth.models import User
from elvis.models.attachment import Attachment
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from elvis.models.collection import Collection
from elvis.models.genre import Genre
from elvis.models.instrumentation import InstrumentVoice
from elvis.models.language import Language
from elvis.models.location import Location
from elvis.models.source import Source
from elvis.models.tag import Tag
from django.core.cache import cache

"""This file contains interdependent serializers which are combined
in order to form function specific serialization. The intent is
to standardize serialization across the project, which will be
hugely useful in terms of maintainability, clarity, and performance.
The serializers are named using the following pattern:

[Model][Variable]Serializer
    -The [Model] is the model this class can serialize
    -The [Variable] is the extent of information to be serialized,
     which include:
        -Min: Only serialize a url, an id, and a human readable title
        -Embed: Serialize links to child models and attachments.
         Primarily intended for use by other serializers.
        -List: Serialize metadata which is useful for sorting
         lists of this model. Include only basic information
         about child models.
        -Full: Serialize all metadata. Intended for detail views."""

#TODO give everything UUIDs so their serialization can be cached.


class CachedMinHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    def to_representation(self, instance, **kwargs):
        # check cache for 'M-' + instance.uuid' and return if found,
        # else call super, cache and return result.
        pass


class AttachmentMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "url")


class ComposerMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('title', 'url', 'id')


class PieceMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Piece
        fields = ('title', 'url', 'id')


class MovementMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Movement
        fields = ('title', 'url', 'id')


class CollectionMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'url', 'id', 'public')


class GenreMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('title', 'id')


class InstrumentVoiceMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentVoice
        fields = ('title', 'id')


class LanguageMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('title', 'id')


class LocationMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('title', 'id')


class SourceMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('title', 'id')


class TagMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', 'id')


class UserMinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'username', 'id')


class AttachmentEmbedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "extension", "url", "source")


class MovementEmbedSerializer(serializers.HyperlinkedModelSerializer):
    composition_end_date = serializers.IntegerField()
    attachments = AttachmentMinSerializer(many=True)
    piece = PieceMinSerializer()

    class Meta:
        model = Movement
        fields = ('title', 'url', 'id', 'attachments', 'composition_end_date',
                  'piece')


class PieceEmbedSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMinSerializer()
    attachments = AttachmentMinSerializer(many=True)
    movements = MovementEmbedSerializer(many=True)

    class Meta:
        model = Piece
        fields = ('title', 'url', 'id', 'composer', 'movements',
                  'movement_count', 'composition_end_date', 'attachments')


class PieceListSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMinSerializer()
    movement_count = serializers.ReadOnlyField()

    class Meta:
        model = Piece
        fields = ('title', 'url', 'id', 'composer',
                  'movement_count', 'composition_end_date')


class MovementListSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMinSerializer()

    class Meta:
        model = Movement
        fields = ('title', 'url', 'id', 'composer', 'composition_end_date')


class ComposerListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer
        fields = ('name', 'url', 'id', 'birth_date', 'death_date',
                  'piece_count', 'movement_count')


class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ('title', 'url', 'id', 'piece_count', 'movement_count')


class AttachmentFullSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "extension", "id", 'source', "url", "created",
                  "updated", "uploader", "attachment")


class ComposerFullSerializer(serializers.HyperlinkedModelSerializer):
    pieces = PieceListSerializer(many=True)
    free_movements = MovementEmbedSerializer(many=True)

    class Meta:
        model = Composer


class CollectionFullSerializer(serializers.HyperlinkedModelSerializer):

    creator = serializers.CharField(source='creator.username')
    pieces = PieceEmbedSerializer(many=True)
    movements = MovementEmbedSerializer(many=True)

    class Meta:
        model = Collection


class MovementFullSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerMinSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    collections = CollectionMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    uploader = serializers.CharField(source='creator.username')

    class Meta:
        model = Piece


class PieceFullSerializer(serializers.HyperlinkedModelSerializer):
    composer = ComposerListSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    collections = CollectionMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    uploader = serializers.CharField(source='creator.username')
    movements = MovementFullSerializer(many=True)

    class Meta:
        model = Piece


class UserFullSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField()
    pieces = PieceListSerializer(many=True)
    movements = MovementListSerializer(many=True)

    class Meta:
        model = User

    def get_full_name(self, obj):
        if not obj.last_name:
            return "{0}".format(obj.username)
        else:
            return "{0} {1}".format(obj.first_name, obj.last_name)
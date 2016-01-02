from rest_framework import serializers
from elvis.models import *

"""These serializers are only to be used by Celery when writing metadata
into download packaged. They are no cached and lack some information."""


class ComposerMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composer
        fields = ('title',)


class GenreMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('title', )


class InstrumentVoiceMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentVoice
        fields = ('title', )


class LanguageMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('title', )


class LocationMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('title', )


class SourceMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('title', )


class TagMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('title', )

class AttachmentEmbedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ("file_name", "extension",  "source")


class MovementFullSerializer(serializers.ModelSerializer):
    composer = ComposerMinSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    creator = serializers.CharField(source='creator.username')

    class Meta:
        model = Movement
        fields = ("title", "composer", "genres", "instruments_voices",
                  "languages", "locations", "sources", "attachments",
                  "creator", "religiosity", "vocalization", "tags")


class PieceFullSerializer(serializers.ModelSerializer):
    composer = ComposerMinSerializer()
    tags = TagMinSerializer(many=True)
    genres = GenreMinSerializer(many=True)
    instruments_voices = InstrumentVoiceMinSerializer(many=True)
    languages = LanguageMinSerializer(many=True)
    locations = LocationMinSerializer(many=True)
    sources = SourceMinSerializer(many=True)
    attachments = AttachmentEmbedSerializer(many=True)
    creator = serializers.CharField(source='creator.username')
    movements = MovementFullSerializer(many=True)

    class Meta:
        model = Piece
        fields = ("title", "composer", "genres", "instruments_voices",
                  "languages", "locations", "sources", "attachments", 
                  "creator", "movements", "religiosity", "vocalization",
                  "tags")
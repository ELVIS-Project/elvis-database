from rest_framework import serializers
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from django.conf import settings
import os

class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.Field(source='pk')
    class Meta:
        model = Movement
        fields = ('url', 'title', "item_id")


class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = ComposerMovementSerializer()
    item_id = serializers.Field(source='pk')
    class Meta:
        model = Piece
        fields = ('url', 'title', 'movements', "item_id", "date_of_composition")


class ComposerSerializer(serializers.HyperlinkedModelSerializer):
    pieces = ComposerPieceSerializer()
    movements = ComposerMovementSerializer()
    image = serializers.SerializerMethodField("retrieve_image")
    item_id = serializers.Field(source='pk')
    
    class Meta:
        model = Composer
        fields = ("url",
                  "id",
                  "old_id",
                  "name",
                  "birth_date",
                  "death_date",
                  "pieces",
                  "created",
                  "updated",
                  "image")

    def retrieve_image(self, obj):
        if not obj.picture:
          return None
        request = self.context.get('request', None)
        path = os.path.relpath(obj.picture.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url

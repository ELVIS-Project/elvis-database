from rest_framework import serializers
from elvis.models.composer import Composer
from elvis.models.piece import Piece
from elvis.models.movement import Movement
from django.conf import settings
import os


class ComposerMovementSerializer(serializers.HyperlinkedModelSerializer):
    item_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = Movement
        fields = ('url', 'item_id', 'title')


class ComposerPieceSerializer(serializers.HyperlinkedModelSerializer):
    movements = ComposerMovementSerializer(many=True)
    item_id = serializers.ReadOnlyField(source='pk')
    date_of_composition = serializers.DateField(format=None)

    class Meta:
        model = Piece
        fields = ('url', 'item_id', 'title', 'movements', "date_of_composition")


class ComposerHistorySerializer(serializers.HyperlinkedModelSerializer):
    history_user_id = serializers.ReadOnlyField()
    updated = serializers.DateTimeField()

    class Meta:
        model = Composer
        fields = ('history_user_id', 'updated')


class ComposerSerializer(serializers.HyperlinkedModelSerializer):
    pieces = ComposerPieceSerializer(many=True)
    movements = ComposerMovementSerializer(many=True)
    image = serializers.SerializerMethodField("retrieve_image")
    item_id = serializers.ReadOnlyField(source='pk')
    birth_date = serializers.DateField(format=None)
    death_date = serializers.DateField(format=None)
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    history = ComposerHistorySerializer(many=True)

    class Meta:
        model = Composer
        fields = ("url",
                  "id",
                  "item_id",
                  "old_id",
                  "name",
                  "birth_date",
                  "death_date",
                  "pieces",
                  "movements",
                  "image",
                  "created",
                  "updated",
                  "history")

    def retrieve_image(self, obj):
        if not obj.picture:
          return None
        request = self.context.get('request', None)
        path = os.path.relpath(obj.picture.path, settings.MEDIA_ROOT)
        url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, path))
        return url


class ComposerListSerializer(serializers.HyperlinkedModelSerializer):
    #image = serializers.SerializerMethodField("retrieve_image")
    item_id = serializers.ReadOnlyField(source='pk')
    birth_date = serializers.DateField(format=None)
    death_date = serializers.DateField(format=None)
    created = serializers.DateTimeField(format=None)
    updated = serializers.DateTimeField(format=None)
    piece_count = serializers.IntegerField()
    movement_count = serializers.IntegerField()

    class Meta:
        model = Composer
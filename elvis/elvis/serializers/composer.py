from rest_framework import serializers
from elvis.models.composer import Composer


class ComposerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Composer

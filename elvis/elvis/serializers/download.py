from rest_framework import serializers
from elvis.models.download import Download


class DownloadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Download

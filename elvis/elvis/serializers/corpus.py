from rest_framework import serializers
from elvis.models.corpus import Corpus


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Corpus

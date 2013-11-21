from rest_framework import serializers
from elvis.serializers.user import UserSerializer
from elvis.models.corpus import Corpus


class CorpusSerializer(serializers.HyperlinkedModelSerializer):
    creator = UserSerializer()
    class Meta:
        model = Corpus

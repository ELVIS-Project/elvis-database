from rest_framework import serializers
from elvis.models.discussion import Discussion


class DiscussionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Discussion

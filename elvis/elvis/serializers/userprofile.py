from rest_framework import serializers
from elvis.models.userprofile import UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile

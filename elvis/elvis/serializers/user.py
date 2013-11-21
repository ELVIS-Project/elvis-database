from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = User

    def get_full_name(self, obj):
        if not obj.last_name:
            return u"{0}".format(obj.username)
        else:
            return u"{0} {1}".format(obj.first_name, obj.last_name)

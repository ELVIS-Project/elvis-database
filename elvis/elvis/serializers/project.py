from rest_framework import serializers
from elvis.models.project import Project


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project

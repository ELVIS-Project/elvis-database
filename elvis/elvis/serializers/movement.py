from rest_framework import serializers
from elvis.models.movement import Movement
from elvis.serializers.composer import ComposerSerializer


class MovementSerializer(serializers.HyperlinkedModelSerializer):

	composer = ComposerSerializer()

	class Meta:
		model = Movement

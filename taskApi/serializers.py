"""
This module contains the serializers for the taskApi app
"""
from django.contrib.auth.models import Group, User
from rest_framework import serializers

from taskApi.models import Dataset, DatasetFile, DatasetRepository


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class DatasetRepositorySerializer(serializers.ModelSerializer):
    """
    DatasetRepository details serializer
    """
    class Meta:
        model = DatasetRepository
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'


class DatasetFileSerializer(serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DatasetFile
        fields = '__all__'

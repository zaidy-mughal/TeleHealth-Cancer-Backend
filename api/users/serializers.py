from rest_framework.serializers import ModelSerializer
from .models import User
from rest_framework import serializers

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role')
        read_only_fields = ('email',)

from rest_framework.serializers import ModelSerializer
from .models import User
from rest_framework import serializers


class UserDetailsSerializer(ModelSerializer):
    """
    User model w/o password
    """

    class Meta:
        model = User
        fields = ("id", "uuid", "email", "first_name", "last_name", "role")
        read_only_fields = ("email", "id", "uuid")

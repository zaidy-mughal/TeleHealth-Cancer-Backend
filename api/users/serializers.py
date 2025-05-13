from .models import User
from rest_framework import serializers


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = User
        fields = ("id", "uuid", "email", "first_name", "last_name", "role")
        read_only_fields = ("id", "uuid", "created_at", "updated_at")


class CheckSerializer(serializers.Serializer):
    """
    Serializer for checking user existence and password match.
    """

    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    
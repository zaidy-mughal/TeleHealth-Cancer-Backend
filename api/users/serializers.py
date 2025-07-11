from .models import User
from rest_framework import serializers
from api.patients.utils.fields import LabelChoiceField
from api.users.choices import Role


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    role = LabelChoiceField(
        choices=Role.choices,
        help_text="Role of the user",
    )

    class Meta:
        model = User
        fields = ("id", "uuid", "email", "first_name","middle_name", "last_name", "role")
        read_only_fields = ("id", "uuid", "created_at", "updated_at")


class CheckSerializer(serializers.Serializer):
    """
    Serializer for checking user existence and password match.
    """

    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

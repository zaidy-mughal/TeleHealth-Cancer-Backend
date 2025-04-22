from rest_framework import serializers
from django.utils import timezone
from api.users.models import User


def validate_email_not_exits(self, email):
    email = email.lower()
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return email


def validate_dob_not_in_future(self, dob):
    if dob > timezone.now().date():
        raise serializers.ValidationError("Date of birth cannot be in the future.")
    return dob

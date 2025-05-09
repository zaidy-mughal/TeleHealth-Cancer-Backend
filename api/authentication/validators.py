import re
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from api.users.models import User
from api.authentication.models import PasswordResetOTP


def validate_min_length(password):
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")


def validate_uppercase(password):
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")


def validate_special_character(password):
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")


def validate_email_not_exits(self, email):
    email = email.lower()
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return email


def validate_dob_not_in_future(self, dob):
    if dob > timezone.now().date():
        raise serializers.ValidationError("Date of birth cannot be in the future.")
    return dob


# OTP related validator
def validate_otp_for_email(email, otp):
    """Validate that the OTP is valid for the given email"""
    try:
        user = User.objects.get(email=email)
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).latest()

        if otp_obj is None:
            return False, None

        is_valid = (
            not otp_obj.is_used
            and otp_obj.created_at >= timezone.now() - timedelta(minutes=2)
        )
        otp_obj.is_used = True
        otp_obj.save()

        return is_valid, otp_obj

    except Exception as e:
        return False, None


def validate_password_match(self, password1, password2):
    """Validate that the two passwords match"""
    if password1 != password2:
        raise serializers.ValidationError("Passwords do not match.")
    return password1


def validate_email_otp_verified(self, user):
    """Validate that the OTP is verified for the given email"""
    verified_otp = PasswordResetOTP.objects.filter(user=user, is_used=True).exists()

    if not verified_otp:
        raise serializers.ValidationError(
            {"email": "You must verify your OTP before changing password"}
        )

    return verified_otp


def validate_email_exits(self, email):
    """Validate that the email exists in the database"""
    email = email.lower()
    if not User.objects.filter(email=email).exists():
        raise serializers.ValidationError("A user with this email does not exist.")
    return email

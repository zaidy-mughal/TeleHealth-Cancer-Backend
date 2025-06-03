import re
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

from api.users.models import User
from api.authentication.models import OTP


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


def validate_otp(email, otp, purpose):
    """Validate that the OTP is valid for the given email"""
    try:
        user = User.objects.get(email=email)
        otp_obj = OTP.objects.filter(user=user, otp=otp, purpose=purpose).latest(
            "created_at"
        )

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


def validate_password_match(self, data):
    password1 = data.get("new_password1")
    password2 = data.get("new_password2")
    """Validate that the two passwords match"""
    if password1 != password2:
        raise serializers.ValidationError("Passwords do not match.")
    return password1


def validate_email_otp_verified(self, user):
    """Validate that the OTP is verified for the given email"""
    verified_otp = OTP.objects.filter(user=user, is_used=True).exists()

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


def validate_email_format(self, data):
    """Validate that the email format is correct"""
    email = data.get("email")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise serializers.ValidationError("Invalid email format.")
    return email


def validate_name_length(self, data):
    """Validate that the name is at least 2 characters long"""

    if len(data.get("first_name", "")) > 30:
        raise serializers.ValidationError(
            {"first_name": "First name cannot exceed 30 characters"}
        )
    if len(data.get("last_name", "")) > 30:
        raise serializers.ValidationError(
            {"last_name": "Last name cannot exceed 30 characters"}
        )
    return data


def validate_doctor_fields(self, data):
    """Validate that the doctor fields are not empty"""
    if not data.get("specialization"):
        raise serializers.ValidationError(
            {"specialization": "Specialization cannot be empty"}
        )
    if not data.get("npi_number"):
        raise serializers.ValidationError({"npi_number": "NPI number cannot be empty"})
    if not data.get("date_of_birth"):
        raise serializers.ValidationError(
            {"date_of_birth": "Date of birth cannot be empty"}
        )
    if not data.get("address"):
        raise serializers.ValidationError({"address": "Address cannot be empty"})
    if "service" not in data or data.get("service") is None:
        raise serializers.ValidationError({"service": "Service cannot be empty"})
    return data


def validate_patient_fields(self, data):
    """Validate that the patient fields are not empty"""
    if not data.get("date_of_birth"):
        raise serializers.ValidationError(
            {"date_of_birth": "Date of birth cannot be empty"}
        )
    if not data.get("phone_number"):
        raise serializers.ValidationError(
            {"phone_number": "Phone number cannot be empty"}
        )
    return data

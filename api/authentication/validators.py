from rest_framework import serializers
from django.utils import timezone
from api.users.models import User
from api.authentication.models import PasswordResetOTP
from datetime import timedelta


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
        
        is_valid = not otp_obj.is_used and otp_obj.created_at >= timezone.now() - timedelta(
                minutes=10
            )
        
        return is_valid, otp_obj

    except User.DoesNotExist:
        return False, None

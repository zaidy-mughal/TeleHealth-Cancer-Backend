import random
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from api.authentication.models import PasswordResetOTP


def create_otp_for_user(user):
    """Create a new OTP for the user, deleting any existing ones"""
    # Delete any existing OTPs for this user
    PasswordResetOTP.objects.filter(user=user).delete()

    # Create random OTP
    otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
    otp_obj = PasswordResetOTP.objects.create(user=user, otp=otp)
    return otp_obj

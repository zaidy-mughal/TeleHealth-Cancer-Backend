from django.core.mail import send_mail
from django.conf import settings


def send_otp_email(user, otp):
    """Send OTP via email"""
    send_mail(
        'Password Reset OTP',
        f'Your OTP for password reset is: {otp}. Valid for 10 minutes.',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
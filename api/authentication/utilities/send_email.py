from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(user, otp):
    """Send OTP via email"""
    try:
        logger.info(f"Attempting to send OTP email to {user.email}")
        logger.debug(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
        
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is: {otp}. Valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        logger.info(f"Successfully sent OTP email to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email: {str(e)}")
        raise
import secrets
import string
from api.authentication.models import OTP
from api.authentication.choices import Purpose


def generate_otp(length=6):
    """Generate a cryptographically secure OTP"""
    alphabet = string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_otp_for_user(user, purpose=Purpose.choices.EMAIL_VERIFICATION):
    """Create a new OTP for the user, deleting any existing ones"""
    OTP.objects.filter(user=user, purpose=purpose).delete()
    otp = generate_otp()
    otp_obj = OTP.objects.create(user=user, otp=otp, purpose=purpose)
    return otp_obj

from django.db import models
from django.conf import settings
from api.base_models import TimeStampMixin
from django.utils import timezone
from api.users.models import User


class PasswordResetOTP(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if OTP is still valid (10 minutes)"""
        return (timezone.now() - self.created_at) < timezone.timedelta(minutes=10)

    class Meta:
        db_table = 'authentication_passwordresetotp'
        get_latest_by = 'created_at'

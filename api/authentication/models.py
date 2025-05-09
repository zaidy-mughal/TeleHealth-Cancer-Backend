from django.db import models
from api.base_models import BaseModel
from django.utils import timezone
from api.users.models import User


class PasswordResetOTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(db_default=False)

    def is_valid(self):
        """Check if OTP is still valid (2 minutes)"""
        return (timezone.now() - self.created_at) < timezone.timedelta(minutes=2)

    class Meta:
        db_table = "passwordresetotp"
        get_latest_by = "created_at"

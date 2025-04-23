from django.db import models
from django.conf import settings
from api.base_models import TimeStampMixin


class PasswordResetOTP(TimeStampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    class Meta:
        get_latest_by = "created_at"

from django.db import models


class Purpose(models.IntegerChoices):
    PASSWORD_RESET = 1, "Password Reset"
    EMAIL_VERIFICATION = 2, "Email Verification"
    TWO_FACTOR_AUTHENTICATION = 3, "Two-Factor Authentication"

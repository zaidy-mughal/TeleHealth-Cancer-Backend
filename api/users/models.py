from django.db import models
from django.contrib.auth.models import AbstractUser
from api.users.choices import Role

from api.base_models import BaseModel
from api.users.managers import UserManager


class User(AbstractUser, BaseModel):
    email = models.EmailField("email address", blank=True, unique=True)
    USERNAME_FIELD = EMAIL_FIELD = "email"
    username = None
    REQUIRED_FIELDS = []
    objects = UserManager()
    role = models.IntegerField(choices=Role.choices, default=Role.PATIENT)

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        db_table = "user"

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from api.users.choices import Role

from api.base_models import BaseModel
from api.users.managers import UserManager


class User(AbstractUser, BaseModel):
    email = models.EmailField(_('email address'), blank=True, unique=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    USERNAME_FIELD = EMAIL_FIELD = 'email'
    username = None
    REQUIRED_FIELDS = []
    objects = UserManager()
    role = models.IntegerField(_('role'), max_length=20, choices=Role.choices, default=Role.PATIENT)

    @property
    def role(self):
        # Groups are treated as roles as groups can be easily assigned access elements.
        user_group = self.groups.first()
        if not user_group:
            return

        return user_group.name

    @property
    def role_type(self):
        user_group = self.groups.first()
        if not user_group:
            return

        return user_group.lh_groups.type

    @property
    def assigned_convener(self):
        user_convener = self.user_convener.first()
        if user_convener is None:
            return

        return user_convener.convener

    @property
    def assigned_practice(self):
        user_practice = self.user_practice.first()
        if user_practice is None:
            return

        return user_practice.practice

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'user'

    def __str__(self):
        return self.email

    def __str__(self):
        return self.email
        

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

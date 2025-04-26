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

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()


# class User(AbstractBaseUser, PermissionsMixin, BaseModel):
#     """
#     An abstract base class implementing a fully featured User model with
#     admin-compliant permissions.

#     Email, uuid and password are required. Other fields are optional.
#     """

#     username_validator = UnicodeUsernameValidator()

#     email = models.CharField(
#         _('email'),
#         max_length=150,
#         unique=True,
#         help_text=_(
#             'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
#         validators=[username_validator, validate_email],
#         error_messages={
#             'unique': _("A user with that username already exists."),
#         },
#     )
#     first_name = models.CharField(_('first name'), max_length=30, blank=True)
#     last_name = models.CharField(_('last name'), max_length=150, blank=True)
#     role = models.IntegerField(_('role'), max_length=20, choices=Role.choices, default=Role.PATIENT)
#     is_staff = models.BooleanField(
#         _('staff status'),
#         default=False,
#         help_text=_(
#             'Designates whether the user can log into this admin site.'),
#     )
#     is_active = models.BooleanField(
#         _('active'),
#         default=True,
#         help_text=_(
#             'Designates whether this user should be treated as active. '
#             'Unselect this instead of deleting accounts.'
#         ),
#     )
#     last_active = models.DateTimeField(_('last_active'), null=True, blank=True)
#     date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

#     USERNAME_FIELD = EMAIL_FIELD = 'email'

#     objects = UserManager()

#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')

#     def get_full_name(self):
#         full_name = f'{self.first_name} {self.last_name}'
#         return full_name.strip()

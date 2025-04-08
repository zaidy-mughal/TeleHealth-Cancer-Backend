import uuid
from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
from django.utils import timezone
from django.contrib.auth.models import UnicodeUsernameValidator

from api.base_models import TimeStampMixin
from api.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Email, uuid and password are required. Other fields are optional.
    """
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    ]

    username_validator = UnicodeUsernameValidator()

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email = models.CharField(
        _('email'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, validate_email],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    date_of_birth = models.DateField(_('date of birth'))
    phone_number = models.IntegerField(
        _('phone number'),
        max_length=15,
    )
    address = models.CharField(_('address'), max_length=255)
    gender = models.CharField(_('gender'), max_length=10, choices=GENDER_CHOICES)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    last_active = models.DateTimeField(_('last_active'), null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = EMAIL_FIELD = 'email'

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

from django.db import models
from api.users.models import User  # Custom User model
from api.base_models import TimeStampMixin


class UserAccount(TimeStampMixin):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )

    VISIT_TYPE_CHOICES = [
        ("New Visitor", "New Visitor"),
        ("Returning Visitor", "Returning Visitor"),
        ("Follow-up Visit", "Follow-up Visit"),
        ("Referral Visit", "Referral Visit"),
        ("Walk-in Visit", "Walk-in Visit"),
        ("Emergency Visit", "Emergency Visit"),
        ("Telemedicine Visit", "Telemedicine Visit"),
    ]

    ROLE_CHOICES = [
        ("PATIENT", "Patient"),
        ("DOCTOR", "Doctor"),
        ("USER", "User"),
    ]

    django_user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, related_name="user_account"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, null=True, blank=True
    )
    visit_type = models.CharField(
        max_length=75, choices=VISIT_TYPE_CHOICES, null=True, blank=True
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="USER")

    def __str__(self):
        return self.email

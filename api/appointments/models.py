# from django.contrib.auth.models import User
from api.users.models import User #adding the custom user
from api.base_models import TimeStampMixin
from django.db import models
from django.utils import timezone
from patients.models import Patient
import uuid

def default_time():
    return timezone.now().time()

class Doctor(TimeStampMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Appointment(TimeStampMixin):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('MISSED', 'Missed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
        ('FAILED', 'Failed'),
    ]

    APPOINTMENT_TYPE_CHOICES = [
        ('GENERAL', 'General Consultation'),
        ('FOLLOW_UP', 'Follow-up'),
        ('EMERGENCY', 'Emergency'),
        ('OTHER', 'Other'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        null=True,
        blank=True
    )
    doctor_name = models.CharField(max_length=100, default="Unknown Doctor")
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=default_time)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    # Appointment details
    reason_for_visit = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Payment and administrative fields
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    phone_fallback = models.BooleanField(default=False)

    # System fields # neglecting these due to TimeStampMixin
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient} with Dr. {self.doctor_name} on {self.date} at {self.time}"

    def can_patient_modify(self):
        """Check if appointment can be modified by patient (24h rule)"""
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return timezone.now() < (appointment_datetime - timezone.timedelta(hours=24))

    def is_missed(self):
        """Check if appointment should be marked as missed (10min rule)"""
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return (self.status == 'SCHEDULED' and
                timezone.now() > (appointment_datetime + timezone.timedelta(minutes=10)))

    class Meta:
        ordering = ['-date', '-time']

class DoctorAvailability(TimeStampMixin):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor', 'day_of_week', 'start_time']

class AvailabilityException(TimeStampMixin):
    # Allowing null for doctor to satisfy migration requirements; update these records later if needed.
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='availability_exceptions',
        null=True,
        blank=True
    )
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=False)  # True to add availability, False to block time

    class Meta:
        ordering = ['date', 'start_time']
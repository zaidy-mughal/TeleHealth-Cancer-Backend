from rest_framework import serializers
from django.utils import timezone


def validate_start_time_lt_end_time(start_time, end_time):
    """
    Validate that the start time is less than the end time.
    """
    if start_time >= end_time:
        raise serializers.ValidationError("Start time must be less than end time.")
    return start_time, end_time


def future_start_time(start_time):
    """
    Validate that the start time is in the future.
    """
    if start_time <= timezone.now():
        raise serializers.ValidationError("Start time must be in the future.")
    return start_time


def validate_user_role(self, user):
    """
    Validate that the user is a doctor.
    """
    if not user.role == 1:
        raise serializers.ValidationError("User must be a doctor.")
    return user

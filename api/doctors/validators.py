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


def validate_booked_slot(value):
    """
    Validate that the time slot is not already booked.
    """
    if value.is_booked:
        raise serializers.ValidationError("This time slot is already booked.")
    return value


def validate_bulk_time_slots(value):
    if not value:
        raise serializers.ValidationError("At least one time slot must be provided.")

    for index, slot_data in enumerate(value):
        slot_num = index + 1
        has_to_delete = "to_delete" in slot_data

        if has_to_delete and not isinstance(slot_data.get("to_delete"), bool):
            raise serializers.ValidationError(
                f"to_delete must be a boolean value in slot #{slot_num}."
            )

        if has_to_delete and not slot_data.get("uuid"):
            raise serializers.ValidationError(
                f"UUID is required for time slots with to_delete field in slot #{slot_num}."
            )

        if not has_to_delete and not slot_data.get("start_time"):
            raise serializers.ValidationError(
                f"start_time is required for time slots in slot #{slot_num}."
            )

        if not has_to_delete and not slot_data.get("end_time"):
            raise serializers.ValidationError(
                f"end_time is required for time slots in slot #{slot_num}."
            )

    return value

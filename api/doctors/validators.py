from datetime import datetime
from rest_framework import serializers
from django.utils import timezone

from api.doctors.models import TimeSlot


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


def validate_time_range(time_range, field_name):
    """Validate time range format"""
    if not isinstance(time_range, dict):
        raise serializers.ValidationError(f"{field_name} must be a dictionary")

    start_time = time_range.get("start_time")
    end_time = time_range.get("end_time")

    if not start_time or not end_time:
        raise serializers.ValidationError(
            f"{field_name} must contain start_time and end_time"
        )

    try:
        start_parsed = datetime.strptime(start_time, "%H:%M").time()
        end_parsed = datetime.strptime(end_time, "%H:%M").time()

        if start_parsed >= end_parsed:
            raise serializers.ValidationError(
                f"{field_name}: start_time must be less than end_time"
            )
    except ValueError:
        raise serializers.ValidationError(
            f"{field_name}: Invalid time format. Use HH:MM format"
        )


def validate_custom_schedule(custom_schedule):
    """
    Validate that the custom schedule is not empty and has valid time slots.
    """
    if not custom_schedule:
        raise serializers.ValidationError(
            "custom_schedule is required when is_custom_days is True"
        )

    valid_days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    for day_schedule in custom_schedule:
        day_name = day_schedule.get("day_name", "").lower()
        if day_name not in valid_days:
            raise serializers.ValidationError(
                f"Invalid day_name: {day_name}. Must be one of {valid_days}"
            )

        if "time_range" not in day_schedule:
            raise serializers.ValidationError(f"time_range is required for {day_name}")
        validate_time_range(day_schedule["time_range"], f"{day_name} time_range")

        if "break_time_range" not in day_schedule:
            raise serializers.ValidationError(
                f"break_time_range is required for {day_name}"
            )
        validate_time_range(
            day_schedule["break_time_range"], f"{day_name} break_time_range"
        )

    return custom_schedule


def validate_invalid_uuids(self, value):
    """
    Validate that the provided UUIDs are valid and exist in the database.
    """
    doctor = self.context["request"].user.doctor
    existing_uuids = set(
        str(uuid)
        for uuid in TimeSlot.objects.filter(doctor=doctor).values_list(
            "uuid", flat=True
        )
    )
    provided_uuids = set(str(uuid) for uuid in value)

    invalid_uuid = provided_uuids - existing_uuids
    if invalid_uuid:
        raise serializers.ValidationError(
            f"Some UUIDs are invalid or don't exist: {list(invalid_uuid)}"
        )
    return value


def validate_booked_slots(self, value):

    doctor = self.context["request"].user.doctor

    booked_uuids = TimeSlot.objects.filter(
        uuid__in=value, doctor=doctor, is_booked=True
    ).values_list("uuid", flat=True)

    if booked_uuids:
        raise serializers.ValidationError(
            f"The following timeslots are already booked: {list(booked_uuids)}"
        )

    return value


def start_month_in_future(start_month):
    """
    Validate that the start month is not in the past.
    """
    current_month = timezone.now().month
    if start_month < current_month:
        raise serializers.ValidationError(
            "Start month must be in the current or future month."
        )
    return start_month


def validate_month_range(start_month, end_month):
    """
    Validate that the start month is less than or equal to the end month.
    """
    if start_month > end_month:
        raise serializers.ValidationError(
            "Start month must be less than or equal to end month."
        )
    return start_month, end_month

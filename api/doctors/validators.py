from datetime import datetime
from rest_framework import serializers
from django.utils import timezone

from api.doctors.choices import Months, DaysOfWeek
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
            "Start month must be less than to end month."
        )
    return start_month, end_month


def validate_request_slot_duplicates(slots_data):
    """
    Check for duplicate time slots within the current request.
    """
    seen_slots = set()
    for slot_data in slots_data:
        slot_key = (
            slot_data['start_time'].replace(microsecond=0),
            slot_data['end_time'].replace(microsecond=0)
        )
        if slot_key in seen_slots:
            raise serializers.ValidationError(
                f"Duplicate timeslot: {slot_data['start_time']} - "
                f"{slot_data['end_time']}"
            )
        seen_slots.add(slot_key)


def validate_request_slot_overlaps(slots_data):
    """
    Check for overlapping time slots within the current request.
    """
    sorted_slots = sorted(slots_data, key=lambda x: x['start_time'])

    for i in range(len(sorted_slots) - 1):
        current_slot = sorted_slots[i]
        next_slot = sorted_slots[i + 1]

        if current_slot['end_time'] > next_slot['start_time']:
            raise serializers.ValidationError(
                f"Overlapping timeslot: "
                f"{current_slot['start_time']} - {current_slot['end_time']} "
                f"Overlaps with {next_slot['start_time']} - "
                f"{next_slot['end_time']}"
            )


def validate_database_duplicates(slots_data, doctor):
    """
    Check for duplicate time slots that already exist in the database.
    """
    for slot_data in slots_data:
        start_time = slot_data['start_time']
        end_time = slot_data['end_time']

        existing_slot = TimeSlot.objects.filter(
            doctor=doctor,
            start_time=start_time,
            end_time=end_time
        ).first()

        if existing_slot:
            raise serializers.ValidationError(
                f"Time slot already exists: {start_time} - "
                f"{end_time}"
            )


def validate_database_overlaps(slots_data, doctor):
    """
    Check for overlapping time slots with existing slots in the database.
    """

    for slot_data in slots_data:
        start_time = slot_data['start_time']
        end_time = slot_data['end_time']

        overlapping_slots = TimeSlot.objects.filter(
            doctor=doctor,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_slots.exists():
            overlapping_slot = overlapping_slots.first()
            raise serializers.ValidationError(
                f"Overlaps timeslot {start_time} - {end_time}"
                f"with"
                f"{overlapping_slot.start_time} - {overlapping_slot.end_time}"
            )


# BULK TIME SLOT VALIDATIONS

def validate_day(value):
    for choice in DaysOfWeek.choices:
        if value.lower() == choice[1].lower():
            return choice[0]
    raise serializers.ValidationError({"detail": "Invalid day of the week"})


def validate_month(value):
    if not isinstance(value, str):
        raise serializers.ValidationError({"detail": "Month must be a string (e.g., "
                                                     "'January')."})
    for choice in Months.choices:
        if value.lower() == choice[1].lower():
            return choice[0]
    raise serializers.ValidationError({"detail": "Invalid Month"})


def validate_start_month_in_future(start_month, year):
    """Validates start month in future"""

    current_date = timezone.now()
    current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0,
                                               microsecond=0)

    try:
        input_date = timezone.make_aware(datetime(year, start_month, 1))
    except ValueError:
        raise serializers.ValidationError("Invalid year or month.")

    print(input_date)
    print(current_month_start)
    if input_date < current_month_start:
        raise serializers.ValidationError("Start month must be in the future.")


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

        if start_parsed < datetime.strptime("03:00", "%H:%M").time():
            raise serializers.ValidationError(
                f"Start time must be greater than 03:00 UTC (8 AM)"
            )

        if end_parsed > datetime.strptime("15:00", "%H:%M").time():
            raise serializers.ValidationError(
                f"End time must be less than 15:00 UTC (8 PM)"
            )

    except ValueError:
        raise serializers.ValidationError(
            f"{field_name}: Invalid time format. Use HH:MM format"
        )


def validate_break_times(break_time_ranges, time_range):
    """Validate break times within time range"""

    time_start = datetime.strptime(time_range["start_time"], "%H:%M").time()
    time_end = datetime.strptime(time_range["end_time"], "%H:%M").time()

    for break_time in break_time_ranges:
        if not isinstance(break_time, dict):
            raise serializers.ValidationError(
                {"detail": "Break time must be a dictionary"})

        start_time = break_time.get("start_time")
        end_time = break_time.get("end_time")

        if not start_time or not end_time:
            raise serializers.ValidationError(
                f"Breaks must contain start_time and end_time"
            )

        break_start = datetime.strptime(break_time["start_time"], "%H:%M").time()
        break_end = datetime.strptime(break_time["end_time"], "%H:%M").time()

        if break_start < time_start or break_end > time_end:
            raise serializers.ValidationError(
                "Break time must be within the working time range"
            )

        if break_start >= break_end:
            raise serializers.ValidationError(
                "Break start time must be less than break end time"
            )


def validate_break_times_overlapp(break_time_ranges):
    """Validate break times overlap"""

    sorted_break_time_ranges = sorted(break_time_ranges, key=lambda x: x['start_time'])

    for i in range(len(sorted_break_time_ranges) - 1):
        current_break_time = sorted_break_time_ranges[i]
        next_break_time = sorted_break_time_ranges[i + 1]

        if current_break_time['end_time'] > next_break_time['start_time']:
            raise serializers.ValidationError(
                f"Overlapping timeslot: "
                f"{current_break_time['start_time']} - "
                f"{current_break_time['end_time']} "
            )


def validate_break_times_duplicate(break_time_ranges):
    """Validate break times duplicate"""
    seen_break_time_ranges = set()
    for break_time_range in break_time_ranges:
        break_key = (
            break_time_range['start_time'],
            break_time_range['end_time']
        )
        if break_key in seen_break_time_ranges:
            raise serializers.ValidationError(
                f"Duplicate timeslot: {break_time_range['start_time']} - "
                f"{break_time_range['end_time']}"
            )


def validate_break_times_within_range(break_time_ranges):
    try:
        for time_range in break_time_ranges:
            work_start = datetime.strptime(time_range["start_time"], "%H:%M").time()
            work_end = datetime.strptime(time_range["end_time"], "%H:%M").time()
            break_start = datetime.strptime(
                time_range["start_time"], "%H:%M"
            ).time()
            break_end = datetime.strptime(time_range["end_time"], "%H:%M").time()

            if break_start < work_start or break_end > work_end:
                raise serializers.ValidationError(
                    "Break time must be within the working time range"
                )

            if break_start >= break_end:
                raise serializers.ValidationError(
                    "Break start time must be less than break end time"
                )

    except ValueError:
        raise serializers.ValidationError("Invalid time format in time ranges")

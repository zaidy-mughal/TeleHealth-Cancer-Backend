import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange

from api.doctors.choices import Services, StateChoices, Months, DaysOfWeek
from api.doctors.models import (
    Doctor,
    Specialization,
    TimeSlot,
    LicenseInfo,
    Service,
    DoctorService,
)
from api.doctors.validators import (
    validate_user_role,
    validate_start_time_lt_end_time,
    future_start_time,
    validate_time_range,
    validate_invalid_uuids,
    validate_booked_slots,
    start_month_in_future,
    validate_day,
    validate_month,
    validate_month_range,
    validate_request_slot_duplicates,
    validate_request_slot_overlaps,
    validate_database_duplicates,
    validate_database_overlaps,
    validate_break_times,
    validate_break_times_overlapp,
    validate_break_times_duplicate,
    validate_start_month_in_future
)
from api.patients.utils.fields import LabelChoiceField
from api.doctors.utils.utils import get_django_weekday_numbers

logger = logging.getLogger(__name__)

User = get_user_model()


class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Specialization model.
    """

    class Meta:
        model = Specialization
        fields = ["name"]


class TimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeSlot model.
    """

    def validate(self, attrs):
        validate_start_time_lt_end_time(attrs["start_time"], attrs["end_time"])
        future_start_time(attrs["start_time"])

        return attrs

    class Meta:
        model = TimeSlot
        fields = ["uuid", "start_time", "end_time", "is_booked"]
        read_only_fields = ["uuid", "is_booked"]

    def create(self, validated_data):
        validated_data["doctor"] = self.context["request"].user.doctor
        return super().create(validated_data)


class TimeSlotCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating time slots.
    This serializer is used to create timeslots weekly.
    """

    time_slots = serializers.ListField(
        child=TimeSlotSerializer(), write_only=True, allow_empty=False
    )

    def validate(self, attrs):
        doctor = self.context["request"].user.doctor
        slots_data = attrs["time_slots"]

        validate_request_slot_duplicates(slots_data)
        validate_request_slot_overlaps(slots_data)
        validate_database_duplicates(slots_data, doctor)
        validate_database_overlaps(slots_data, doctor)

        return super().validate(self, attrs)

    @transaction.atomic
    def create(self, validated_data):
        try:
            slots_data = self.validated_data["time_slots"]
            doctor = self.context["request"].user.doctor

            slots = [TimeSlot(doctor=doctor, **slot) for slot in slots_data]

            created_slots = TimeSlot.objects.bulk_create(slots, batch_size=10)
            count = len(created_slots)

            return count

        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError("Error creating time slots")


class TimeSlotDeleteSerializer(serializers.Serializer):
    """
    Serializer for deleting timeslots weekly.
    """

    time_slot_uuids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, allow_empty=False
    )

    def validate_time_slot_uuids(self, value):
        validate_invalid_uuids(self, value)
        validate_booked_slots(self, value)
        return value

    @transaction.atomic
    def delete_timeslots(self):
        try:
            uuids = self.validated_data["time_slot_uuids"]
            doctor = self.context["request"].user.doctor

            deleted_count, _ = TimeSlot.objects.filter(
                uuid__in=uuids, doctor=doctor, is_booked=False
            ).delete()

            return deleted_count
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(f"Error deleting timeslots")


class LicenseInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the LicenseInfo model.
    """

    state = LabelChoiceField(choices=StateChoices.choices)

    class Meta:
        model = LicenseInfo
        fields = ["license_number", "state", "doctor"]
        read_only_fields = ["doctor"]

    def create(self, validated_data):
        validated_data["doctor"] = self.context["request"].user.doctor
        return super().create(validated_data)


class ServiceSerializer(serializers.ModelSerializer):
    name = LabelChoiceField(choices=Services.choices)

    class Meta:
        model = Service
        fields = ["id", "uuid", "name"]
        read_only_fields = ["id", "uuid"]


class DoctorServiceSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = DoctorService
        fields = ["doctor", "service"]

    def to_representation(self, instance):
        service_data = ServiceSerializer(instance.service).data
        return {"doctor": instance.doctor.uuid, "service": service_data["name"]}


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Doctor model.
    """

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        write_only=True,
    )

    services = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()
    specialization = SpecializationSerializer(read_only=True)
    time_slots = serializers.SerializerMethodField()

    def get_services(self, obj):
        services = obj.doctor_services.all()
        serializer = DoctorServiceSerializer(services, many=True)
        return [item["service"] for item in serializer.data]

    def get_states(self, obj):
        licenses = obj.license_info.all()
        serializer = LicenseInfoSerializer(licenses, many=True)
        return [item["state"] for item in serializer.data]

    def get_time_slots(self, obj):
        available_slots = obj.time_slots.filter(
            is_booked=False, start_time__gte=timezone.now()
        ).order_by("start_time")

        return TimeSlotSerializer(available_slots, many=True).data

    def validate_user(self, user):
        return validate_user_role(self, user)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "uuid",
            "user",
            "first_name",
            "last_name",
            "specialization",
            "states",
            "services",
            "date_of_birth",
            "address",
            "npi_number",
            "time_slots",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "first_name",
            "last_name",
            "states",
            "services",
            "time_slots",
            "created_at",
            "updated_at",
        ]


class DayScheduleSerializer(serializers.Serializer):
    day = serializers.CharField(max_length=10, required=True, allow_blank=False)
    break_times = serializers.ListField(
        child=serializers.DictField(), required=True, max_length=3
    )
    time_range = serializers.DictField(required=True, allow_empty=False)

    def validate(self, attrs):
        validate_time_range(attrs["time_range"], 'time_range')
        validate_break_times(attrs["break_times"], attrs["time_range"])
        validate_break_times_overlapp(attrs["break_times"])
        validate_break_times_duplicate(attrs["break_times"])
        attrs["day"] = validate_day(attrs["day"])
        return attrs


class BulkTimeSlotCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating time slots for multiple months.
    """

    start_month = serializers.CharField(max_length=10, required=True,
                                        allow_blank=False)
    end_month = serializers.CharField(max_length=10, required=True,
                                      allow_blank=False)

    days_of_week = serializers.ListField(
        child=DayScheduleSerializer(), allow_empty=False, required=True, max_length=7
    )

    year = serializers.IntegerField(
        default=timezone.now().year,
        min_value=2000,
        max_value=timezone.now().year + 10,
        required=False,
    )

    def validate(self, attrs):
        start_month = validate_month(attrs['start_month'])
        end_month = validate_month(attrs["end_month"])
        year = attrs['year']

        validate_start_month_in_future(start_month, year)
        validate_month_range(start_month, end_month)

        attrs['start_month'] = start_month
        attrs['end_month'] = end_month

        return attrs

    @staticmethod
    def _parse_time(time_str):
        return datetime.strptime(time_str, "%H:%M").time()

    @transaction.atomic
    def save(self):
        try:
            doctor = self.context['request'].user.doctor
            validated_data = self.validated_data
            year = validated_data.get("year", timezone.now().year)
            start_month = validated_data.get("start_month")
            end_month = validated_data.get("end_month")

            today = timezone.now().date()
            timeslot_objects = []

            # Map Django weekday int 0 to the corresponding schedule of the day
            weekday_schedules = {
                schedule["day"]: schedule for schedule in
                validated_data["days_of_week"]
            }

            for month in range(start_month, end_month + 1):
                _, num_days_in_month = monthrange(year, month)

                for day in range(1, num_days_in_month + 1):
                    date_obj = datetime(year, month, day).date()

                    if date_obj < today:
                        continue

                    weekday_index = date_obj.weekday()
                    if weekday_index not in weekday_schedules:
                        continue

                    schedule = weekday_schedules[weekday_index]

                    day_start_time = self._parse_time(
                        schedule["time_range"]["start_time"])
                    day_end_time = self._parse_time(schedule["time_range"]["end_time"])

                    break_periods = [
                        (self._parse_time(break_time["start_time"]),
                         self._parse_time(break_time["end_time"]))
                        for break_time in schedule["break_times"]
                    ]

                    current_slot_start = datetime.combine(date_obj, day_start_time)
                    day_end_datetime = datetime.combine(date_obj, day_end_time)

                    while current_slot_start + timedelta(
                            minutes=30) <= day_end_datetime:
                        current_slot_end = current_slot_start + timedelta(minutes=30)

                        # check current slot overlaps with any break period
                        overlaps_with_break = any(
                            current_slot_start.time() < break_end and
                            current_slot_end.time() > break_start
                            for break_start, break_end in break_periods
                        )

                        if not overlaps_with_break:
                            timeslot_objects.append(TimeSlot(
                                doctor=doctor,
                                start_time=timezone.make_aware(current_slot_start),
                                end_time=timezone.make_aware(current_slot_end),
                                is_booked=False
                            ))

                        current_slot_start = current_slot_end

            if timeslot_objects:
                created_slots = TimeSlot.objects.bulk_create(timeslot_objects,
                                                             batch_size=200)
                return {
                    "created_count": len(created_slots),
                    "total_months": end_month - start_month,
                    "message": f"Successfully created {len(created_slots)} time "
                               f"slots.",
                }

            return {
                "created_count": 0,
                "total_months": end_month - start_month,
                "message": "No time slots were created (possibly all dates are in "
                           "the past).",
            }

        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError("Error creating time slots")


class BulkTimeSlotDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk deleting time slots within a date range for specific days of
    the week.
    """

    start_month = serializers.ChoiceField(
        choices=Months.choices, validators=[start_month_in_future], required=True
    )
    end_month = serializers.ChoiceField(choices=Months.choices, required=True)
    days_of_week = serializers.ListField(
        child=serializers.ChoiceField(choices=DaysOfWeek.choices), allow_empty=False
    )
    year = serializers.IntegerField(
        default=timezone.now().year,
        min_value=2000,
        max_value=timezone.now().year + 10,
        required=False,
    )

    def validate(self, attrs):
        start_month = attrs["start_month"]
        end_month = attrs["end_month"]

        validate_month_range(start_month, end_month)

        return attrs

    @transaction.atomic
    def delete_timeslots(self):
        try:
            validated_data = self.validated_data
            doctor = self.context["request"].user.doctor

            year = validated_data.get("year")
            start_month = validated_data["start_month"]
            end_month = validated_data["end_month"]

            start_date = timezone.make_aware(datetime(year, start_month, 1))

            # Calculate last day of end month
            if end_month == 12:
                end_date = timezone.make_aware(
                    datetime(year + 1, 1, 1) - timedelta(days=1)
                )
            else:
                end_date = timezone.make_aware(
                    datetime(year, end_month + 1, 1) - timedelta(days=1)
                )

            end_date = end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            django_weekdays = get_django_weekday_numbers(
                validated_data["days_of_week"]
            )

            all_matching_slots = TimeSlot.objects.filter(
                doctor=doctor,
                start_time__gte=start_date,
                start_time__lte=end_date,
                start_time__week_day__in=django_weekdays,
            )

            unbooked_slots = all_matching_slots.filter(is_booked=False)
            booked_slots = all_matching_slots.filter(is_booked=True)

            deleted_slots_data = unbooked_slots.values_list("uuid", flat=True)

            booked_slots_data = booked_slots.values_list(
                "uuid", "start_time", "end_time", "is_booked"
            )

            deleted_count, _ = unbooked_slots.delete()

            return {
                "deleted_count": deleted_count,
                "deleted_slots": deleted_slots_data,
                "booked_slots_count": booked_slots.count(),
                "booked_slots": booked_slots_data,
                "message": f"Successfully deleted unbooked time slots. Booked slots "
                           f"cannot be deleted.",
            }

        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError("Error deleting timeslots")

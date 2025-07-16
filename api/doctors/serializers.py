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
    validate_month_range,
    validate_break_time_within_range,
    validate_request_slot_duplicates,
    validate_request_slot_overlaps,
    validate_database_duplicates,
    validate_database_overlaps,
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


class BulkTimeSlotCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating time slots for multiple months.
    """

    start_month = serializers.ChoiceField(
        choices=Months.choices, validators=[start_month_in_future]
    )
    end_month = serializers.ChoiceField(choices=Months.choices)

    days_of_week = serializers.ListField(
        child=serializers.ChoiceField(choices=DaysOfWeek.choices), allow_empty=False
    )
    year = serializers.IntegerField(
        default=timezone.now().year,
        min_value=2000,
        max_value=timezone.now().year + 10,
        required=False,
    )

    time_range = serializers.DictField(required=True, allow_empty=False)
    break_time_range = serializers.DictField(required=True, allow_empty=False)

    def validate(self, attrs):
        start_month = attrs["start_month"]
        end_month = attrs["end_month"]

        validate_month_range(start_month, end_month)
        validate_time_range(attrs["time_range"], "time_range")
        validate_time_range(attrs["break_time_range"], "break_time_range")
        validate_break_time_within_range(
            attrs["time_range"], attrs["break_time_range"]
        )

        return attrs

    def _generate_time_slots_for_one_day(self, date, time_range, break_time_range,
                                         doctor):
        """Generate 30-minute time slots for a given date"""
        slots = []

        # get formatted times, create datetime and attach timezone with all
        start_time = datetime.strptime(time_range["start_time"], "%H:%M").time()
        end_time = datetime.strptime(time_range["end_time"], "%H:%M").time()
        break_start = datetime.strptime(break_time_range["start_time"], "%H:%M").time()
        break_end = datetime.strptime(break_time_range["end_time"], "%H:%M").time()

        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        break_start_datetime = datetime.combine(date, break_start)
        break_end_datetime = datetime.combine(date, break_end)

        current_time = timezone.make_aware(current_time)
        end_datetime = timezone.make_aware(end_datetime)
        break_start_datetime = timezone.make_aware(break_start_datetime)
        break_end_datetime = timezone.make_aware(break_end_datetime)

        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=30)

            is_during_break = not (
                    slot_end <= break_start_datetime or current_time >=
                    break_end_datetime)
            is_in_past = current_time <= timezone.now()
            is_last_slot = slot_end > end_datetime

            if is_during_break or is_in_past:
                current_time = slot_end
                continue

            if is_last_slot:
                break

            slots.append(
                TimeSlot(
                    doctor=doctor,
                    start_time=current_time,
                    end_time=slot_end,
                    is_booked=False,
                )
            )
            current_time = slot_end

        return slots

    @transaction.atomic
    def create_time_slots(self):
        try:
            validated_data = self.validated_data
            doctor = self.context["request"].user.doctor

            year = validated_data.get("year")
            start_month = validated_data["start_month"]
            end_month = validated_data["end_month"]
            days_of_week = validated_data["days_of_week"]
            time_range = validated_data["time_range"]
            break_time_range = validated_data["break_time_range"]

            python_weekdays = get_django_weekday_numbers(days_of_week)
            all_slots = []

            current_month = start_month
            current_year = year

            while True:
                days_in_month = monthrange(current_year, current_month)[1]

                # Generate slots for each day in the month
                for day in range(1, days_in_month + 1):
                    date = datetime(current_year, current_month, day).date()

                    is_unwanted_weekday = date.weekday() not in python_weekdays
                    is_past_date = date < timezone.now().date()

                    if is_unwanted_weekday or is_past_date:
                        continue

                    slots = self._generate_time_slots_for_one_day(
                        date, time_range, break_time_range, doctor
                    )
                    all_slots.extend(slots)

                if current_month == end_month:
                    break

                current_month += 1

            if all_slots:
                created_slots = TimeSlot.objects.bulk_create(all_slots, batch_size=100)
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
        choices=Months.choices, validators=[start_month_in_future]
    )
    end_month = serializers.ChoiceField(choices=Months.choices)
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

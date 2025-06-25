from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
import calendar

from api.doctors.choices import Services, StateChoices
from api.doctors.models import (
    Doctor,
    Specialization,
    TimeSlot,
    LicenseInfo,
    Service,
    DoctorService,
)
from api.doctors.validators import (
    validate_bulk_time_slots,
    validate_user_role,
    validate_start_time_lt_end_time,
    future_start_time,
    validate_custom_schedule,
    validate_time_range,
)
from api.patients.utils.fields import LabelChoiceField

User = get_user_model()


class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Specialization model.
    """

    class Meta:
        model = Specialization
        fields = ["name"]


# will add validations to timeslot in doctor
class TimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeSlot model.
    """

    def validate(self, attrs):
        """
        Validate timeslots for the doctor.
        """
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


class TimeSlotBulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk deleting timeslots.
    """

    time_slot_uuids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    def validate_time_slot_uuids(self, value):
        if not value:
            raise serializers.ValidationError("At least one UUID must be provided.")

        doctor = self.context["request"].user.doctor

        # Get existing timeslots for this doctor
        existing_timeslots = TimeSlot.objects.filter(uuid__in=value, doctor=doctor)

        existing_uuids = set(
            str(uuid) for uuid in existing_timeslots.values_list("uuid", flat=True)
        )
        provided_uuids = set(str(uuid) for uuid in value)
        # Check for invalid UUIDs
        invalid_uuids = provided_uuids - existing_uuids
        if invalid_uuids:
            raise serializers.ValidationError(
                f"Some UUIDs are invalid or don't exist: {list(invalid_uuids)}"
            )

        booked_timeslots = existing_timeslots.filter(is_booked=True)
        if booked_timeslots.exists():
            raise serializers.ValidationError(
                "Cannot delete timeslots that are already booked."
                " Some of the provided timeslots are already booked."
            )

        return value

    def delete_timeslots(self):
        """
        Delete the validated timeslots.
        """
        try:
            uuids = self.validated_data["time_slot_uuids"]
            doctor = self.context["request"].user.doctor

            deleted_count, _ = TimeSlot.objects.filter(
                uuid__in=uuids, doctor=doctor, is_booked=False
            ).delete()

            return deleted_count
        except Exception as e:
            raise serializers.ValidationError(f"Error deleting timeslots: {str(e)}")


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
        available_slots = obj.time_slots.all()
        return TimeSlotSerializer(
            available_slots.order_by("start_time"), many=True
        ).data

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

    no_of_months = serializers.IntegerField(min_value=1, max_value=12)
    is_custom_days = serializers.BooleanField(default=False)

    time_range = serializers.DictField(required=False, allow_empty=False)
    break_time_range = serializers.DictField(required=False, allow_empty=False)

    custom_schedule = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=False
    )

    def validate(self, attrs):
        is_custom_days = attrs.get("is_custom_days", False)

        if is_custom_days:
            validate_custom_schedule(attrs.get("custom_schedule"))
        else:
            if not attrs.get("time_range"):
                raise serializers.ValidationError(
                    "time_range is required when is_custom_days is False"
                )
            if not attrs.get("break_time_range"):
                raise serializers.ValidationError(
                    "break_time_range is required when is_custom_days is False"
                )
            validate_time_range(attrs["time_range"], "time_range")
            validate_time_range(attrs["break_time_range"], "break_time_range")

        return attrs

    def _generate_time_slots(self, date, time_range, break_time_range, doctor):
        """Generate 30-minute time slots for a given date"""
        slots = []

        # Parse time strings
        start_time = datetime.strptime(time_range["start_time"], "%H:%M").time()
        end_time = datetime.strptime(time_range["end_time"], "%H:%M").time()
        break_start = datetime.strptime(break_time_range["start_time"], "%H:%M").time()
        break_end = datetime.strptime(break_time_range["end_time"], "%H:%M").time()

        # Create datetime objects for the specific date
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        break_start_datetime = datetime.combine(date, break_start)
        break_end_datetime = datetime.combine(date, break_end)

        # Make timezone aware
        current_time = timezone.make_aware(current_time)
        end_datetime = timezone.make_aware(end_datetime)
        break_start_datetime = timezone.make_aware(break_start_datetime)
        break_end_datetime = timezone.make_aware(break_end_datetime)

        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=30)

            # Skip if slot overlaps with break time
            if not (
                slot_end <= break_start_datetime or current_time >= break_end_datetime
            ):
                current_time = slot_end
                continue

            # Skip if slot would exceed end time
            if slot_end > end_datetime:
                break

            # Skip if slot is in the past
            if current_time <= timezone.now():
                current_time = slot_end
                continue

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

    def create_time_slots(self):
        """Create time slots based on the validated data"""
        request = self.context["request"]
        doctor = request.user.doctor

        validated_data = self.validated_data
        no_of_months = validated_data["no_of_months"]
        is_custom_days = validated_data["is_custom_days"]

        all_slots = []
        current_date = timezone.now().date()

        # Generate slots for specified number of months
        for month_offset in range(no_of_months):
            # Calculate the target month and year
            target_month = current_date.month + month_offset
            target_year = current_date.year

            # Handle year overflow
            while target_month > 12:
                target_month -= 12
                target_year += 1

            # Get the number of days in the target month
            days_in_month = monthrange(target_year, target_month)[1]

            # Generate slots for each weekday in the month
            for day in range(1, days_in_month + 1):
                date = datetime(target_year, target_month, day).date()

                # Skip weekends (Monday=0, Sunday=6)
                if date.weekday() >= 5:  # Saturday=5, Sunday=6
                    continue

                # Skip past dates
                if date < current_date:
                    continue

                if is_custom_days:
                    # Find schedule for this specific day
                    day_name = calendar.day_name[date.weekday()].lower()
                    day_schedule = next(
                        (
                            schedule
                            for schedule in validated_data["custom_schedule"]
                            if schedule["day_name"].lower() == day_name
                        ),
                        None,
                    )

                    if day_schedule:
                        slots = self._generate_time_slots(
                            date,
                            day_schedule["time_range"],
                            day_schedule["break_time_range"],
                            doctor,
                        )
                        all_slots.extend(slots)
                else:
                    # Use same schedule for all weekdays
                    slots = self._generate_time_slots(
                        date,
                        validated_data["time_range"],
                        validated_data["break_time_range"],
                        doctor,
                    )
                    all_slots.extend(slots)

        # Bulk create all slots
        if all_slots:
            created_slots = TimeSlot.objects.bulk_create(all_slots, batch_size=100)
            return created_slots

        return []

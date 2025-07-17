from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError

from api.doctors.choices import StateChoices, Services
from api.doctors.models import Doctor, Service, TimeSlot


class DoctorFilter(filters.FilterSet):
    state = filters.CharFilter(method="filter_by_state")
    service = filters.CharFilter(method="filter_by_service")
    date = filters.DateFilter(field_name="time_slots__start_time__date")
    doctor_uuid = filters.UUIDFilter(field_name="uuid")

    class Meta:
        model = Doctor
        fields = ["state", "service", "date", "doctor_uuid"]

    def filter_by_state(self, queryset, name, value):
        try:
            state_value = next(
                choice.value
                for choice in StateChoices
                if choice.label.lower() == value.lower()
            )
        except StopIteration:
            raise ValidationError(f"Invalid state: {value}")
        return queryset.filter(license_info__state=state_value)

    def filter_by_service(self, queryset, name, value):
        try:
            service_value = next(
                choice.value
                for choice in Services
                if choice.label.lower() == value.lower()
            )
            service = Service.objects.filter(name=service_value).first()
            if service:
                return queryset.filter(doctor_services__service=service)
            return queryset
        except StopIteration:
            raise ValidationError(f"Invalid service: {value}")


class TimeSlotFilter(filters.FilterSet):
    state = filters.CharFilter(method="filter_by_state")
    service = filters.CharFilter(method="filter_by_service")
    doctor_uuid = filters.UUIDFilter(field_name="doctor__uuid")

    class Meta:
        model = TimeSlot
        fields = ["state", "service", "doctor_uuid"]

    def filter_by_state(self, queryset, name, value):
        try:
            state_value = next(
                choice.value
                for choice in StateChoices
                if choice.label.lower() == value.lower()
            )
        except StopIteration:
            raise ValidationError(f"Invalid state: {value}")
        return queryset.filter(doctor__license_info__state=state_value)

    def filter_by_service(self, queryset, name, value):
        try:
            service_value = next(
                choice.value
                for choice in Services
                if choice.label.lower() == value.lower()
            )
            service = Service.objects.filter(name=service_value).first()
            if service:
                return queryset.filter(doctor__doctor_services__service=service)
            return queryset
        except StopIteration:
            raise ValidationError(f"Invalid service: {value}")

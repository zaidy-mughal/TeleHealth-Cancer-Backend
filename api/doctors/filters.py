from django_filters import rest_framework as filters
from django.core.exceptions import ValidationError

from api.doctors.choices import StateChoices
from api.doctors.models import Doctor


class DoctorFilter(filters.FilterSet):
    state = filters.CharFilter(method="filter_by_state")
    service = filters.UUIDFilter(method="filter_by_service")

    class Meta:
        model = Doctor
        fields = ["state", "service"]

    def filter_by_state(self, queryset, name, value):
        try:
            state_value = next(
                choice.value
                for choice in StateChoices
                if choice.label.lower() == value.lower()
            )
        except StopIteration:
            raise ValidationError(f"Invalid state: {value}")
        return queryset.filter(license_info__state=state_value).distinct()

    def filter_by_service(self, queryset, name, value):
        return queryset.filter(doctor_services__service__uuid=value).distinct()

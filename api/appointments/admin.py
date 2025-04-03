from django.contrib import admin
from .models import Doctor, Appointment, DoctorAvailability, AvailabilityException

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'specialty')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialty')
    list_filter = ('specialty',)
    raw_id_fields = ('user',)  # Use a raw_id widget for the related user

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_full_name.short_description = 'Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Replace direct field names with custom methods where needed.
    list_display = ('id', 'get_patient', 'get_doctor_name', 'date', 'time', 'status', 'is_paid')
    list_filter = ('status', 'is_paid')
    search_fields = (
        'patient__user__username',
        'doctor__user__first_name',
        'doctor__user__last_name',
        'reason_for_visit'
    )
    date_hierarchy = 'date'

    def get_patient(self, obj):
        """
        Return the username of the patient associated with the appointment.
        Adjust this method if you need to display a different patient attribute.
        """
        if hasattr(obj, 'patient') and obj.patient and hasattr(obj.patient, 'user'):
            return obj.patient.user.username
        return 'N/A'
    get_patient.short_description = 'Patient'

    def get_doctor_name(self, obj):
        """
        Return the doctor's full name from the associated user.
        """
        if obj.doctor and hasattr(obj.doctor, 'user'):
            return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"
        return 'N/A'
    get_doctor_name.short_description = 'Doctor Name'


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')


@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available', 'date')
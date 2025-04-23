from django.contrib import admin
from api.appointments.models import Appointments


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment_date', 'appointment_time', 'status']
    readonly_fields = ['created_at', 'updated_at']

    def doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    doctor_name.short_description = 'Doctor'

    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'

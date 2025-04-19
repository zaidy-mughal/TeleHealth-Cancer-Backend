from django.contrib import admin
from .models import Appointments


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = (
        'doctor_name',
        'patient_name',
        'appointment_date',
        'appointment_time',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = ('status', 'appointment_date', 'doctor', 'patient')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name',
                     'patient__user__first_name', 'patient__user__last_name')
    ordering = ('-appointment_date', '-appointment_time')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    doctor_name.short_description = 'Doctor'

    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'

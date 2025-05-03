from django.contrib import admin
from api.appointments.models import Appointments
from api.appointments.choices import Status

@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'uuid', 'doctor_name', 'patient_name', 'appointment_start', 'appointment_end', 'status_display']
    list_filter = ['status', 'doctor', 'patient', 'created_at']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name', 
                    'patient__user__first_name', 'patient__user__last_name']
    date_hierarchy = 'created_at'
    raw_id_fields = ['doctor', 'patient', 'time_slot']
    
    def doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    doctor_name.short_description = 'Doctor'
    
    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'
    
    def appointment_start(self, obj):
        return obj.time_slot.start_time if hasattr(obj.time_slot, 'start') else '-'
    appointment_start.short_description = 'Start'
    
    def appointment_end(self, obj):
        return obj.time_slot.end_time if hasattr(obj.time_slot, 'end') else '-'
    appointment_start.short_description = 'End'
    
    def status_display(self, obj):
        return Status(obj.status).label
    status_display.short_description = 'Status'
    
    fieldsets = [
        ('Appointment Details', {
            'fields': ['doctor', 'patient', 'time_slot', 'status']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    readonly_fields = ['uuid', 'created_at', 'updated_at']

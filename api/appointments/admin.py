from django.contrib import admin
from api.appointments.models import Appointment
from api.appointments.choices import Status


@admin.register(Appointment)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "uuid",
        "doctor_name",
        "patient_name",
        "follow_up_of",
        "appointment_type",
        "appointment_start",
        "appointment_end",
        "status_display",
    ]
    list_filter = ["status", "created_at"]
    search_fields = [
        "time_slot__doctor__user__first_name",
        "time_slot__doctor__user__last_name",
        "medical_record__patient__user__first_name",
        "medical_record__patient__user__last_name",
    ]
    date_hierarchy = "created_at"

    def doctor_name(self, obj):
        return obj.time_slot.doctor.user.get_full_name()

    doctor_name.short_description = "Doctor"

    def patient_name(self, obj):
        return obj.medical_record.patient.user.get_full_name()

    patient_name.short_description = "Patient"

    def appointment_start(self, obj):
        return obj.time_slot.start_time if hasattr(obj.time_slot, "start") else "-"

    appointment_start.short_description = "Start"

    def appointment_end(self, obj):
        return obj.time_slot.end_time if hasattr(obj.time_slot, "end") else "-"

    appointment_start.short_description = "End"

    def status_display(self, obj):
        return Status(obj.status).label

    status_display.short_description = "Status"

    fieldsets = [
        ("Appointment Details", {"fields": ["time_slot", "status"]}),
        ("Metadata", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
    readonly_fields = ["uuid", "created_at", "updated_at"]

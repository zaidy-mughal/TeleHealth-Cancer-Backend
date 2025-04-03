from django.contrib import admin
from .models import UserAccount
from api.patients.models import Patient
from api.appointments.models import Doctor


class UserAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "created_at",
        "get_profile_details",
    )
    list_filter = ("role", "created_at", "gender", "visit_type")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "full_name", "password", "role")}),
        ("Personal Information", {"fields": ("date_of_birth", "gender", "visit_type")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_profile_details(self, obj):
        try:
            if obj.role == "PATIENT":
                patient = Patient.objects.get(user=obj.user)
                return f"Patient: {patient.physician_name or 'No Physician'}"
            elif obj.role == "DOCTOR":
                doctor = Doctor.objects.get(user=obj.user)
                return f"Doctor: {doctor.specialty or 'No Specialty'}"
        except:
            return "No Profile"

    get_profile_details.short_description = "Profile Details"


# Remove the duplicate registrations
admin.site.register(UserAccount, UserAccountAdmin)

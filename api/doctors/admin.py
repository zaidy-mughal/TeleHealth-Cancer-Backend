from django.contrib import admin
from api.doctors.models import Doctor, Specialization, TimeSlot, LicenseInfo

admin.site.register(LicenseInfo)

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "name"]
    readonly_fields = ["id", "uuid", "created_at", "updated_at"]

    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "doctor", "start_time", "end_time", "is_booked"]
    readonly_fields = ["id", "uuid", "created_at", "updated_at"]

    search_fields = ("doctor__user__first_name", "doctor__user__last_name")
    ordering = ("-created_at",)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ["id", "uuid", "get_name", "get_email", "get_specialization"]
    readonly_fields = ["id", "uuid", "created_at", "updated_at"]

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = "Name"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_specialization(self, obj):
        return obj.specialization.name if obj.specialization else None
    get_specialization.short_description = "Specialization"

    search_fields = ("get_name", "get_email")
    ordering = ("-created_at",)

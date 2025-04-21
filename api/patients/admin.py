from django.contrib import admin

from api.patients.models import (
    Patient, IodineAllergy, Allergy, Medication, MedicalHistory,
    AddictionHistory, SurgicalHistory, CancerHistory, CancerType,
    Pharmacist, PrimaryPhysician
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_name', 'get_email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

    def get_name(self, obj):
        return obj.user.get_full_name()
    get_name.short_description = 'Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(IodineAllergy)
admin.site.register(Allergy)
admin.site.register(Medication)
admin.site.register(MedicalHistory)
admin.site.register(AddictionHistory)
admin.site.register(SurgicalHistory)
admin.site.register(CancerHistory)
admin.site.register(CancerType)
admin.site.register(Pharmacist)
admin.site.register(PrimaryPhysician)

from django.contrib import admin
from api.doctors.models import Doctor, Specialization, TimeSlot, LicenseInfo

admin.site.register(Doctor)
admin.site.register(Specialization)
admin.site.register(TimeSlot)
admin.site.register(LicenseInfo)

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'get_full_name', 
        'get_username', 
        'email', 
        'phone_number'
    )
    search_fields = (
        'first_name', 
        'middle_name', 
        'last_name', 
        'email', 
        'phone_number', 
        'user__username'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 
                'middle_name', 
                'last_name', 
                'email', 
                'phone_number'
            )
        }),
        ('Address', {
            'fields': (
                'address', 
                'city', 
                'state', 
                'zipcode'
            )
        }),
        ('Healthcare Providers', {
            'fields': (
                'physician_name', 
                'physician_contact_number', 
                'pharmacist_name', 
                'pharmacist_contact_number'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        middle = f" {obj.middle_name}" if obj.middle_name else ""
        return f"{obj.first_name}{middle} {obj.last_name}"

    get_full_name.short_description = 'Full Name'

    def get_username(self, obj):
        return obj.user.username if obj.user else ""

    get_username.short_description = 'Username'
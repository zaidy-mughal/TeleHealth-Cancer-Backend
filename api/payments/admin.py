from django.contrib import admin
from .models import (
    AppointmentPayment,
    AppointmentPaymentRefund,
    RefundPolicy,
)

@admin.register(AppointmentPayment)
class AppointmentPaymentAdmin(admin.ModelAdmin):
    list_display = ("uuid", "appointment", "stripe_payment_intent_id", 
                    "status", "created_at", "updated_at")
    search_fields = ("uuid", "stripe_payment_intent_id")
    list_filter = ("status", "created_at", "updated_at")
    raw_id_fields = ("appointment",)

@admin.register(AppointmentPaymentRefund)
class AppointmentPaymentRefundAdmin(admin.ModelAdmin):
    list_display = ("uuid", "appointment_payment", "refund_policy", 
                    "amount", "reason", "created_at")
    search_fields = ("uuid", "reason")
    list_filter = ("refund_policy", "created_at")
    raw_id_fields = ("appointment_payment",)

@admin.register(RefundPolicy)
class RefundPolicyAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "refund_type", "hours_before_min", 
                    "hours_before_max", "created_at", "updated_at")
    search_fields = ("uuid", "name")
    list_filter = ("refund_type", "created_at", "updated_at")
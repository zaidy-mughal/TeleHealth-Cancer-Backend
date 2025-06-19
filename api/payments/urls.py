from django.urls import path
from api.payments.views import (
    CreatePaymentIntentView,
    AppointmentRefundView,
    StripeWebhookView,
    AppointmentPaymentUUIDView,
)

urlpatterns = [
    path(
        "stripe/create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    path("stripe/refund/", AppointmentRefundView.as_view(), name="stripe-refund"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path('payment-uuid/<uuid:appointment_uuid>/', AppointmentPaymentUUIDView.as_view()),
]

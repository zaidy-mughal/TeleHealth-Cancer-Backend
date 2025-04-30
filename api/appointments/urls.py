from django.urls import path, include
from api.appointments.views import AppointmentCreateView, AppointmentRetrieveView

urlpatterns = [
    path('create/', AppointmentCreateView.as_view(), name='create-appointment'),
    path('retrieve/<str:patient_uuid>/', AppointmentRetrieveView.as_view(), name='get-appointments'),
]

from django.urls import path, include
from api.appointments.views import AppointmentView

urlpatterns = [
    path('create/', AppointmentView.as_view(), name='create-appointment'),
    path('retrieve/<str:patient_id>/', AppointmentView.as_view(), name='get-appointments'),
]

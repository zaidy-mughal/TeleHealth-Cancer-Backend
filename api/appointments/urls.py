from django.urls import path, include
from .views import AppointmentView

urlpatterns = [
    path('create/', AppointmentView.as_view(), name='create-appointment'),
    path('<str:patient_id>/', AppointmentView.as_view(), name='get-appointments'),
]

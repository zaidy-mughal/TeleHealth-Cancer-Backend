from django.urls import path, include
from api.appointments.views import AppointmentCreateView, PatientAppointmentRetrieveView, DoctorAppointmentRetrieveView
from api.patients.models import Patient

urlpatterns = [
    path('create/', AppointmentCreateView.as_view(), name='create-appointment'),    
    path('patient/', PatientAppointmentRetrieveView.as_view(), name='get-appointments-patient'),
    path('doctor/', DoctorAppointmentRetrieveView.as_view(), name='get-appointment-doctor'),
]

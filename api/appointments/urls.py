from pydoc import Doc
from django.urls import path
from api.appointments.views import (
    AppointmentCreateView, 
    PatientAppointmentListView,
    AppointmentDetailView,
    DoctorAppointmentListView
)


urlpatterns = [
    path("create/", AppointmentCreateView.as_view(), name="create-appointment"),
    path("patient/", PatientAppointmentListView.as_view(), name="patient-appointments-list"),
    path("<uuid:uuid>/", AppointmentDetailView.as_view(), name="appointment-detail"),
    path("doctor/", DoctorAppointmentListView.as_view(), name="doctor-appointments-list"),
]

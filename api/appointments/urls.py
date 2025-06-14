from django.urls import path
from api.appointments.views import (
    PatientAppointmentListView,
    AppointmentDetailView,
    DoctorAppointmentListView,
    RescheduleAppointmentView
)


urlpatterns = [
    path("patient/", PatientAppointmentListView.as_view(), name="patient-appointments-list"),
    path("<uuid:uuid>/", AppointmentDetailView.as_view(), name="appointment-detail"),
    path("doctor/", DoctorAppointmentListView.as_view(), name="doctor-appointments-list"),
    path("<uuid:uuid>/reschedule/", RescheduleAppointmentView.as_view(), name="appointment-reschedule"),
]

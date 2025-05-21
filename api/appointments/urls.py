from django.urls import path
from api.appointments.views import AppointmentCreateView, AppointmentRetrieveView


urlpatterns = [
    path("create/", AppointmentCreateView.as_view(), name="create-appointment"),
    path("", AppointmentRetrieveView.as_view(), name="get-appointments"),
]

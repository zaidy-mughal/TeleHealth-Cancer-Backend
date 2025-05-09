from django.urls import path, include

from api.patients.views import (
    PatientRetreiveView,
)


urlpatterns = [
    path("me/", PatientRetreiveView.as_view(), name="patient"),
]
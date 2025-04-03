from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet, DoctorViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet)
router.register(r'doctors', DoctorViewSet)

urlpatterns = [
    path('appoint/', include(router.urls)),
]
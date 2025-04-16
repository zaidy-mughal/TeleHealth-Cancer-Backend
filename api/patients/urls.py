from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet

router = DefaultRouter()
router.register(r"patients", PatientViewSet)

urlpatterns = [
    path("patient/", include(router.urls)),
]

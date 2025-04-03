# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserAccountViewSet

router = DefaultRouter()
router.register(r"accounts", UserAccountViewSet, basename="useraccount")

urlpatterns = [
    path("sign_in/", include(router.urls)),
]

from django.urls import path, include
from .views import CustomRegisterView, CustomLoginView

urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='custom_register'),
    path('login/', CustomLoginView.as_view(), name='custom_login'),
    path('', include('dj_rest_auth.urls')),
]

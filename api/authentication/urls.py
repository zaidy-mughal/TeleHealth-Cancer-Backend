from django.urls import path, include
from api.authentication.views import CustomRegisterView, CustomLoginView

urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', include('dj_rest_auth.urls'), name='token_refresh'),
    path('', include('dj_rest_auth.urls')),
]

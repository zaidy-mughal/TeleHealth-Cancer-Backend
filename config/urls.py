from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.http import JsonResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('api.authentication.urls')),
    path('api/users/', include('api.users.urls')),
    path('api/appointments/', include('api.appointments.urls')),
    path('api/doctors/', include('api.doctors.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('health/', lambda request: JsonResponse({'status': 'ok'})),
    path('', lambda request: JsonResponse({'status': 'ok'})),
]

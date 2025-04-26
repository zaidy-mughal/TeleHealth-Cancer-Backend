from django.urls import path
from api.doctors.views import SpecializationListCreateView

urlpatterns = [
    path('specializations/', SpecializationListCreateView.as_view(), name='specialization-list-create'),
] 
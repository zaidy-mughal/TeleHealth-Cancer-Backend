from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from api.doctors.serializers import SpecializationSerializer
from api.doctors.models import Specialization
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Doctors"],
    request=SpecializationSerializer,
    responses=SpecializationSerializer,
    description="API for managing doctor specializations.",
)
class SpecializationListCreateView(ListCreateAPIView):
    """
    API view to handle specialization creation and listing.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()

# Create your views here.

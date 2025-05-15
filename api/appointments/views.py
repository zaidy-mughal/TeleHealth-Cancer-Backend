from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.appointments.serializers import AppointmentSerializer
from api.appointments.models import Appointments
from api.patients.models import Patient
from api.doctors.permissions import IsDoctorOrAdmin
from api.doctors.models import TimeSlot
from api.patients.permissions import IsPatientOrAdmin

import logging
logger = logging.getLogger(__name__)

@extend_schema(
    tags=["Appointments"],
    request=AppointmentSerializer,
    responses=AppointmentSerializer(many=True),
    description="API for managing appointments.",
)
@method_decorator(csrf_exempt, name="dispatch")
class PatientAppointmentRetrieveView(RetrieveAPIView):
    """
    API view to handle appointment creation and retrieval.
    Includes validation for appointments and proper error handling.
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve appointments with optional filtering.
        """
        try:
            
            patient = request.user.patient
            appointments = Appointments.objects.filter(patient=patient)

            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error retrieving appointments: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



@extend_schema(
    tags=["Appointments"],
    request=AppointmentSerializer,
    responses=AppointmentSerializer(many=True),
    description="API for managing appointments.",
)
@method_decorator(csrf_exempt, name="dispatch")
class DoctorAppointmentRetrieveView(RetrieveAPIView):
    """
    API view to handle appointment retrieval with doctor uuid.
    Includes validation for appointments and proper error handling.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve appointments with filtering.
        """
        try:
            doctor = request.user.doctor            
            appointments = Appointments.objects.filter(time_slot__doctor=doctor)

            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving appointments: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )




@extend_schema(
    tags=["Appointments"],
    request=AppointmentSerializer,
    description="API for managing appointments.",
)
@method_decorator(csrf_exempt, name="dispatch")
class AppointmentCreateView(CreateAPIView):
    """
    API view to handle appointment creation.
    Includes validation for appointments and proper error handling.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer


    def post(self, request):
        """
        Create a new appointment with validation.
        """
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            appointment = serializer.save()

            return Response(
                self.serializer_class(appointment).data, status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error creating appointment: {str(e)}")
            return Response(
                {"error": f"Failed to create appointment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


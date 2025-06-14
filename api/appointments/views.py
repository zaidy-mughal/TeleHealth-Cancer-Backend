from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from api.appointments.serializers import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
    DoctorAppointmentSerializer,
    RescheduleAppointmentSerializer,
)
from django.shortcuts import get_object_or_404
from api.appointments.models import Appointment
from api.doctors.permissions import IsDoctorOrAdmin
from api.patients.permissions import IsPatientOrAdmin

import logging
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Appointments"],
    responses=AppointmentSerializer,
    description="API for retrieving a single appointment by UUID.",
)
class PatientAppointmentListView(RetrieveAPIView):
    """
    API view to retrieve appointments for a specific patient.
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        try:
            patient = request.user.patient
            appointments = Appointment.objects.filter(patient=patient)
            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving patient appointments: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve patient appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["Appointments"],
    responses=AppointmentDetailSerializer,
    description="API for retrieving a single appointment by UUID.",
)
@method_decorator(csrf_exempt, name="dispatch")
class AppointmentDetailView(RetrieveAPIView):
    """
    API view to retrieve a single appointment by UUID.
    Returns detailed appointment information including patient data.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentDetailSerializer
    lookup_field = "uuid"

    def get_object(self):
        uuid = self.kwargs["uuid"]
        appointment = get_object_or_404(Appointment, uuid=uuid)

        return appointment


@extend_schema(
    tags=["Appointments"],
    responses=DoctorAppointmentSerializer,
    description="API for retrieving a single appointment by UUID.",
)
class DoctorAppointmentListView(RetrieveAPIView):
    """
    API view to retrieve appointments for a specific doctor.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = DoctorAppointmentSerializer

    def get(self, request, *args, **kwargs):
        try:
            doctor = request.user.doctor
            appointments = Appointment.objects.filter(time_slot__doctor=doctor)
            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving doctor appointments: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve doctor appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@extend_schema(
    tags=["Appointments"],
    responses=RescheduleAppointmentSerializer,
    description="API for rescheduling an appointment by UUID.",
)
class RescheduleAppointmentView(UpdateAPIView):
    """
    API view to reschedule an existing appointment by UUID.
    """
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = RescheduleAppointmentSerializer
    lookup_field = "uuid"

    def get_object(self):
        uuid = self.kwargs["uuid"]
        return get_object_or_404(Appointment, uuid=uuid)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        logger.info(f"Rescheduling completed for appointment {instance.uuid}: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()
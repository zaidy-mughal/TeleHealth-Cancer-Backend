from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from api.appointments.serializers import (
    AppointmentSerializer,
    AppointmentDetailSerializer,
    DoctorAppointmentSerializer,
)
from api.patients.serializers import (
    IodineAllergySerializer,
    AllergyListSerializer,
    MedicationListSerializer,
    MedicalHistoryListSerializer,
    SurgicalHistoryListSerializer,
    CareProviderListSerializer,
    AddictionHistoryListSerializer,
    CancerHistoryListSerializer,
)

from django.shortcuts import get_object_or_404
from api.appointments.models import Appointment
from api.doctors.permissions import IsDoctorOrAdmin
from api.patients.permissions import IsPatientOrAdmin
from api.patients.views import BaseMedicalRecordFieldUpdateView

import logging
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class PatientAppointmentListView(RetrieveAPIView):
    """
    API view to retrieve appointments for a specific patient.
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        try:
            patient = request.user.patient
            appointments = Appointment.objects.filter(
                medical_record__patient=patient, status__in=[1, 2, 3]
            )
            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving patient appointments: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve patient appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


class AppointmentCreateView(CreateAPIView):
    """
    API view to create a new appointment.
    This view allows patients to book appointments with doctors.
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = AppointmentSerializer


@method_decorator(csrf_exempt, name="dispatch")
class IodineAllergyAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = IodineAllergySerializer


@method_decorator(csrf_exempt, name="dispatch")
class AllergyBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = AllergyListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicationBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = MedicationListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicalHistoryBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = MedicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SurgicalHistoryBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = SurgicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CareProviderBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = CareProviderListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AddictionHistoryBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = AddictionHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CancerHistoryBulkAppointmentUpdateView(BaseMedicalRecordFieldUpdateView):
    is_appointment_update = True
    serializer_class = CancerHistoryListSerializer

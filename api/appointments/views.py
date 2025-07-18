from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

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
from api.doctors.permissions import IsDoctor
from api.patients.permissions import IsPatient
from api.patients.views import BaseMedicalRecordFieldUpdateRetrieveView
from api.utils.exception_handler import HandleExceptionAPIView

import logging

logger = logging.getLogger(__name__)


class PatientAppointmentListView(HandleExceptionAPIView, RetrieveAPIView):
    """
    API view to retrieve appointments for a specific patient.
    """

    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):

        patient = request.user.patient
        appointments = Appointment.objects.filter(
            medical_record__patient=patient, status__in=[1, 2, 3]
        )
        serializer = self.serializer_class(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AppointmentDetailView(HandleExceptionAPIView, RetrieveAPIView):
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


class DoctorAppointmentListView(HandleExceptionAPIView, RetrieveAPIView):
    """
    API view to retrieve appointments for a specific doctor.
    """

    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = DoctorAppointmentSerializer

    def get(self, request, *args, **kwargs):

        doctor = request.user.doctor
        appointments = Appointment.objects.filter(time_slot__doctor=doctor)
        serializer = self.serializer_class(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentCreateView(HandleExceptionAPIView, CreateAPIView):
    """
    API view to create a new appointment.
    This view allows patients to book appointments with doctors.
    """

    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = AppointmentSerializer


@method_decorator(csrf_exempt, name="dispatch")
class IodineAllergyAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = IodineAllergySerializer


@method_decorator(csrf_exempt, name="dispatch")
class AllergyBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = AllergyListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicationBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = MedicationListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicalHistoryBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = MedicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SurgicalHistoryBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = SurgicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CareProviderBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = CareProviderListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AddictionHistoryBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = AddictionHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CancerHistoryBulkAppointmentUpdateRetrieveView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = CancerHistoryListSerializer

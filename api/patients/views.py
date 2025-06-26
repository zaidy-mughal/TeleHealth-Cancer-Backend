from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from api.patients.permissions import IsPatientOrAdmin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.patients.serializers import (
    PatientSerializer,
    IodineAllergySerializer,
    AllergyListSerializer,
    MedicationListSerializer,
    MedicalHistoryListSerializer,
    SurgicalHistoryListSerializer,
    CareProviderListSerializer,
    AddictionHistoryListSerializer,
    CancerHistoryListSerializer,
)

import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class BaseMedicalRecordFieldUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    serializer_class = None
    is_appointment_update = False

    def get_serializer_context(self, request):
        return {
            "request": request,
            "is_appointment_update": self.is_appointment_update,
        }

    def patch(self, request):
        try:
            serializer = self.serializer_class(
                data=request.data,
                context=self.get_serializer_context(request),
            )
            serializer.is_valid(raise_exception=True)

            updated_record = serializer.update(None, serializer.validated_data)

            return Response(
                {f"Successfully Updated: {updated_record}"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error updating medical record field: {str(e)}")
            return Response(
                {"detail": f"Failed to update medical record field: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class IodineAllergyUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = IodineAllergySerializer


@method_decorator(csrf_exempt, name="dispatch")
class AllergyBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = AllergyListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicationBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = MedicationListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicalHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = MedicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SurgicalHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = SurgicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CareProviderBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = CareProviderListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AddictionHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = AddictionHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CancerHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateView):
    serializer_class = CancerHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class PatientRetreiveView(RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def get_object(self):
        return self.request.user.patient

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


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

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from api.patients.permissions import IsPatient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from api.utils.exception_handler import HandleExceptionAPIView
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
class BaseMedicalRecordFieldUpdateView(HandleExceptionAPIView, APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = None
    is_appointment_update = False

    def get_serializer_context(self, request):
        return {
            "request": request,
            "is_appointment_update": self.is_appointment_update,
        }

    def patch(self, request):

        serializer = self.get_serializer_class()(
            data=request.data,
            context=self.get_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(None, serializer.validated_data)
        return Response({"message": "Successfully Updated"},
                        status=status.HTTP_200_OK)


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
class PatientRetreiveView(HandleExceptionAPIView, RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_object(self):
        return self.request.user.patient

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

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
class BaseMedicalRecordFieldUpdateRetrieveView(HandleExceptionAPIView, APIView):
    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = None

    def get_serializer_context(self, request):
        appointment_uuid = self.kwargs.get("uuid")
        if appointment_uuid:
            return {
                "request": request,
                "appointment_uuid": appointment_uuid,
            }
        return {"request": request}

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context=self.get_serializer_context(request),
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(None, serializer.validated_data)
        return Response({"message": "Successfully Updated"},
                        status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            {}, context=self.get_serializer_context(request)
        )
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )


@method_decorator(csrf_exempt, name="dispatch")
class IodineAllergyUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = IodineAllergySerializer


@method_decorator(csrf_exempt, name="dispatch")
class AllergyBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = AllergyListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicationBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = MedicationListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class MedicalHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = MedicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SurgicalHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = SurgicalHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CareProviderBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = CareProviderListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class AddictionHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = AddictionHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class CancerHistoryBulkUpdateView(BaseMedicalRecordFieldUpdateRetrieveView):
    serializer_class = CancerHistoryListSerializer


@method_decorator(csrf_exempt, name="dispatch")
class PatientRetreiveView(HandleExceptionAPIView, RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_object(self):
        return self.request.user.patient

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

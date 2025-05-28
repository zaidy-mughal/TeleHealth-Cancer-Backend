from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.patients.serializers import (
    PatientSerializer,
    IodineAllergySerializer,
    PatientAllergySerializer,
    PatientMedicationSerializer,
    PatientMedicalHistorySerializer,
    PatientSurgicalHistorySerializer,
    PatientCareProviderSerializer,
    PatientAddictionHistorySerializer,
    CancerHistorySerializer,
    CancerHistoryListSerializer,
)
from api.patients.models import IodineAllergy, CancerHistory
from api.patients.permissions import IsPatientOrAdmin

import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class IodineAllergyViewSet(viewsets.ModelViewSet):
    serializer_class = IodineAllergySerializer
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_queryset(self):
        return IodineAllergy.objects.filter(patient=self.request.user.patient)

    def get_object(self):
        return get_object_or_404(IodineAllergy, patient=self.request.user.patient)


class PatientAllergyViewSet(viewsets.ViewSet):
    """
    Handles creating and updating allergies for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_allergies(self, request):
        serializer = PatientAllergySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_allergies(self, request):
        serializer = PatientAllergySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PatientMedicationViewSet(viewsets.ViewSet):
    """
    Handles creating and updating medications for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_medications(self, request):
        serializer = PatientMedicationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_medications(self, request):
        serializer = PatientMedicationSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PatientMedicalHistoryViewSet(viewsets.ViewSet):
    """
    Handles creating and updating medical history for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_medical_history(self, request):
        serializer = PatientMedicalHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_medical_history(self, request):
        serializer = PatientMedicalHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


class PatientSurgicalHistoryViewSet(viewsets.ViewSet):
    """
    Handles creating and updating surgical history for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_surgical_history(self, request):
        serializer = PatientSurgicalHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_surgical_history(self, request):
        serializer = PatientSurgicalHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


class PatientCareProviderViewSet(viewsets.ViewSet):
    """
    Handles creating and updating care providers for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_care_providers(self, request):
        serializer = PatientCareProviderSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_care_providers(self, request):
        serializer = PatientCareProviderSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class CancerHistoryBulkViewSet(viewsets.ViewSet):
    """
    Handles creating and updating cancer history for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_cancer_history(self, request):
        serializer = CancerHistoryListSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_cancer_history(self, request):
        serializer = CancerHistoryListSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PatientAddictionHistoryViewSet(viewsets.ViewSet):
    """
    Handles creating and updating addiction history for the current user (patient).
    """

    permission_classes = [IsAuthenticated, IsPatientOrAdmin]
    http_method_names = ["post", "put"]

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["post"], url_path="create")
    def create_addiction_history(self, request):
        serializer = PatientAddictionHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.create(serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"], url_path="update")
    def update_addiction_history(self, request):
        serializer = PatientAddictionHistorySerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.update(
            instance=None, validated_data=serializer.validated_data
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PatientRetreiveView(RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def get_object(self):
        return self.request.user.patient

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.patients.serializers import PatientSerializer
from api.patients.permissions import IsPatientOrAdmin

import logging
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class PatientRetreiveView(RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def get_object(self):
        return self.request.user.patient

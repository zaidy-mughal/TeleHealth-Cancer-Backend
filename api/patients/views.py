from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from api.patients.serializers import PatientSerializer


class PatientRetreiveView(RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.patient

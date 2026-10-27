from rest_framework import viewsets

from .models import Patient
from .serializers import PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    CRUD for patients.

    POST   /api/patients/       create a patient
    GET    /api/patients/       list the patients created by the current user
    GET    /api/patients/<id>/  retrieve one patient
    PUT    /api/patients/<id>/  update (PATCH for partial update)
    DELETE /api/patients/<id>/  delete
    """

    serializer_class = PatientSerializer

    def get_queryset(self):
        # Users can only ever see / touch the patients they created.
        return Patient.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

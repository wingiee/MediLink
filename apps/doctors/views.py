from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Doctor
from .permissions import IsCreatorOrReadOnly
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    """
    CRUD for doctors.

    POST   /api/doctors/       add a doctor
    GET    /api/doctors/       list all doctors
    GET    /api/doctors/<id>/  retrieve one doctor
    PUT    /api/doctors/<id>/  update (creator only)
    DELETE /api/doctors/<id>/  delete (creator only)
    """

    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.models import Patient

from .models import PatientDoctorMapping
from .serializers import MappingSerializer, PatientDoctorSerializer


class MappingListCreateView(ListCreateAPIView):
    """
    POST /api/mappings/  assign a doctor to a patient
    GET  /api/mappings/  list all mappings of the current user's patients
    """

    serializer_class = MappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingDetailView(APIView):
    """
    GET    /api/mappings/<patient_id>/  all doctors assigned to that patient
    DELETE /api/mappings/<id>/          remove a doctor from a patient (mapping id)
    """

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk, created_by=request.user)
        mappings = patient.doctor_mappings.select_related("doctor")
        return Response(
            {
                "patient": patient.id,
                "patient_name": patient.name,
                "doctors": PatientDoctorSerializer(mappings, many=True).data,
            }
        )

    def delete(self, request, pk):
        mapping = get_object_or_404(
            PatientDoctorMapping, pk=pk, patient__created_by=request.user
        )
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import serializers

from apps.doctors.serializers import DoctorSerializer
from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    """Accepts patient / doctor ids on input, returns nested details on output."""

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "created_at")
        read_only_fields = ("id", "created_at")
        # We raise our own, friendlier duplicate error below
        validators = []

    def validate_patient(self, patient):
        user = self.context["request"].user
        if patient.created_by_id != user.id:
            raise serializers.ValidationError("You can only assign doctors to your own patients.")
        return patient

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(
            patient=attrs["patient"], doctor=attrs["doctor"]
        ).exists():
            raise serializers.ValidationError("This doctor is already assigned to this patient.")
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["patient"] = PatientSerializer(instance.patient).data
        data["doctor"] = DoctorSerializer(instance.doctor).data
        return data


class PatientDoctorSerializer(serializers.ModelSerializer):
    """Mapping row seen from a patient: id of the mapping + the doctor's details."""

    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "doctor", "created_at")

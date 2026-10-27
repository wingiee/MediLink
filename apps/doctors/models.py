from django.conf import settings
from django.db import models


class Doctor(models.Model):
    class Specialization(models.TextChoices):
        CARDIOLOGY = "cardiology", "Cardiology"
        DERMATOLOGY = "dermatology", "Dermatology"
        NEUROLOGY = "neurology", "Neurology"
        ORTHOPEDICS = "orthopedics", "Orthopedics"
        PEDIATRICS = "pediatrics", "Pediatrics"
        PSYCHIATRY = "psychiatry", "Psychiatry"
        GENERAL = "general", "General Medicine"
        OTHER = "other", "Other"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors"
    )
    name = models.CharField(max_length=150)
    specialization = models.CharField(
        max_length=50, choices=Specialization.choices, default=Specialization.GENERAL
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"Dr. {self.name} - {self.get_specialization_display()}"

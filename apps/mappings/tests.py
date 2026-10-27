"""End-to-end API tests covering auth, patients, doctors and mappings."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.doctors.models import Doctor
from apps.patients.models import Patient

User = get_user_model()

PATIENT = {"name": "Ravi Kumar", "age": 34, "gender": "M", "phone": "9876543210"}
DOCTOR = {"name": "Anita Sharma", "specialization": "cardiology", "email": "anita@clinic.com"}


class BaseAPITestCase(APITestCase):
    def make_user(self, email="user@example.com", password="StrongPass123!"):
        return User.objects.create_user(
            username=email, email=email, password=password, first_name="Test"
        )

    def login(self, user):
        resp = self.client.post(
            "/api/auth/login/", {"email": user.email, "password": "StrongPass123!"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['tokens']['access']}")


class AuthTests(BaseAPITestCase):
    def test_register_and_login(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"name": "Asha", "email": "asha@example.com", "password": "StrongPass123!"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(
            "/api/auth/login/", {"email": "asha@example.com", "password": "StrongPass123!"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data["tokens"])

    def test_duplicate_email_rejected(self):
        self.make_user("dup@example.com")
        resp = self.client.post(
            "/api/auth/register/",
            {"name": "X", "email": "dup@example.com", "password": "StrongPass123!"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_password_rejected(self):
        self.make_user("a@example.com")
        resp = self.client.post("/api/auth/login/", {"email": "a@example.com", "password": "nope"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_protected_endpoints_require_token(self):
        for url in ("/api/patients/", "/api/doctors/", "/api/mappings/"):
            self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)


class PatientTests(BaseAPITestCase):
    def setUp(self):
        self.user = self.make_user()
        self.login(self.user)

    def test_crud(self):
        resp = self.client.post("/api/patients/", PATIENT)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        pid = resp.data["id"]
        self.assertEqual(len(self.client.get("/api/patients/").data), 1)
        resp = self.client.patch(f"/api/patients/{pid}/", {"age": 35})
        self.assertEqual(resp.data["age"], 35)
        self.assertEqual(self.client.delete(f"/api/patients/{pid}/").status_code, 204)

    def test_user_cannot_see_other_users_patients(self):
        other = self.make_user("other@example.com")
        Patient.objects.create(created_by=other, **PATIENT)
        self.assertEqual(len(self.client.get("/api/patients/").data), 0)


class DoctorTests(BaseAPITestCase):
    def setUp(self):
        self.user = self.make_user()
        self.login(self.user)

    def test_crud(self):
        resp = self.client.post("/api/doctors/", DOCTOR)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        did = resp.data["id"]
        self.assertEqual(self.client.get(f"/api/doctors/{did}/").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/doctors/{did}/").status_code, 204)

    def test_only_creator_can_modify(self):
        other = self.make_user("other@example.com")
        doctor = Doctor.objects.create(created_by=other, **DOCTOR)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor.id}/").status_code, 200)
        self.assertEqual(
            self.client.patch(f"/api/doctors/{doctor.id}/", {"name": "Hacked"}).status_code, 403
        )


class MappingTests(BaseAPITestCase):
    def setUp(self):
        self.user = self.make_user()
        self.login(self.user)
        self.patient = Patient.objects.create(created_by=self.user, **PATIENT)
        self.doctor = Doctor.objects.create(created_by=self.user, **DOCTOR)

    def assign(self):
        return self.client.post(
            "/api/mappings/", {"patient": self.patient.id, "doctor": self.doctor.id}
        )

    def test_full_flow(self):
        resp = self.assign()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        mapping_id = resp.data["id"]

        self.assertEqual(len(self.client.get("/api/mappings/").data), 1)

        resp = self.client.get(f"/api/mappings/{self.patient.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["doctors"][0]["doctor"]["email"], DOCTOR["email"])

        self.assertEqual(self.client.delete(f"/api/mappings/{mapping_id}/").status_code, 204)
        self.assertEqual(len(self.client.get("/api/mappings/").data), 0)

    def test_duplicate_assignment_rejected(self):
        self.assign()
        self.assertEqual(self.assign().status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_to_foreign_patient(self):
        other = self.make_user("other@example.com")
        foreign = Patient.objects.create(created_by=other, **PATIENT)
        resp = self.client.post(
            "/api/mappings/", {"patient": foreign.id, "doctor": self.doctor.id}
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

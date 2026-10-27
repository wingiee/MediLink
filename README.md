# 🏥 Patient-Doctor Management System

A secure REST API built with **Django REST Framework**, **PostgreSQL** and **JWT authentication**
that lets users register, manage patients and doctors, and assign doctors to patients.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

---

## ✨ Features

- 🔐 Register / login with email + password, JWT access & refresh tokens (`djangorestframework-simplejwt`)
- 🧑‍🤝‍🧑 Full CRUD for **patients** (private per user: you only see the patients you created)
- 🩺 Full CRUD for **doctors** (visible to all authenticated users, editable only by their creator)
- 🔗 **Patient ↔ Doctor mapping** with duplicate protection and ownership checks
- 🛡️ Every endpoint except register/login requires a valid JWT
- 🗄️ PostgreSQL via Django ORM, config through environment variables
- 🌐 Clean web interface served at `/` (login, patients, doctors, assignments)
- ✅ Automated test-suite + ready-to-import Postman collection

---

## 📁 Project Structure

```
patient-doctor-management/
├── manage.py
├── requirements.txt
├── docker-compose.yml          # one-command PostgreSQL
├── .env.example                # environment template
├── config/                     # project settings, root urls, wsgi/asgi
│   ├── settings.py
│   └── urls.py
├── templates/
│   └── index.html              # web UI (single page, talks to the API)
├── apps/
│   ├── accounts/               # register, login, token refresh
│   ├── patients/               # Patient model + CRUD API
│   ├── doctors/                # Doctor model + CRUD API (+ custom permission)
│   └── mappings/               # PatientDoctorMapping model, API and tests
└── docs/
    └── postman_collection.json # import into Postman
```

Each app follows the same layout: `models.py → serializers.py → views.py → urls.py`.

---

## 🚀 Setup

```bash
# 1. Clone and enter the project
cd patient-doctor-management

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start PostgreSQL (Docker) – or use your own local PostgreSQL
docker compose up -d

# 5. Configure environment
cp .env.example .env              # Windows: copy .env.example .env

# 6. Create tables and run
python manage.py makemigrations accounts patients doctors mappings
python manage.py migrate
python manage.py runserver
```

Open the website at **http://127.0.0.1:8000/** (register, log in, manage patients, doctors and assignments).
The REST API itself lives at **http://127.0.0.1:8000/api/**

Using your own PostgreSQL instead of Docker? Create the database first:
`CREATE DATABASE patient_doctor_db;` and put your credentials in `.env`.

### Run the tests
```bash
python manage.py test
```

---

## 📡 API Reference

All endpoints (except register & login) need the header:
`Authorization: Bearer <access_token>`

### 1. Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register with `name`, `email`, `password` |
| POST | `/api/auth/login/` | Login with `email`, `password` → JWT tokens |
| POST | `/api/auth/token/refresh/` | Get a new access token using `refresh` |

### 2. Patients (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/patients/` | Add a new patient |
| GET | `/api/patients/` | List patients created by the current user |
| GET | `/api/patients/<id>/` | Patient details |
| PUT / PATCH | `/api/patients/<id>/` | Update patient |
| DELETE | `/api/patients/<id>/` | Delete patient |

### 3. Doctors (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/doctors/` | Add a new doctor |
| GET | `/api/doctors/` | List all doctors |
| GET | `/api/doctors/<id>/` | Doctor details |
| PUT / PATCH | `/api/doctors/<id>/` | Update doctor (creator only) |
| DELETE | `/api/doctors/<id>/` | Delete doctor (creator only) |

### 4. Patient-Doctor Mappings (authenticated)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mappings/` | Assign a doctor to a patient |
| GET | `/api/mappings/` | List all mappings |
| GET | `/api/mappings/<patient_id>/` | All doctors assigned to a patient |
| DELETE | `/api/mappings/<id>/` | Remove a doctor from a patient (`<id>` = mapping id) |

---

## 🧪 Example Requests

**Register**
```json
POST /api/auth/register/
{ "name": "Demo User", "email": "demo@example.com", "password": "StrongPass123!" }
```

**Login → response**
```json
{
  "message": "Login successful.",
  "user": { "id": 1, "name": "Demo User", "email": "demo@example.com" },
  "tokens": { "refresh": "eyJ...", "access": "eyJ..." }
}
```

**Create patient**
```json
POST /api/patients/
{ "name": "Ravi Kumar", "age": 34, "gender": "M", "phone": "9876543210",
  "address": "Agra, UP", "medical_history": "Hypertension" }
```

**Create doctor**
```json
POST /api/doctors/
{ "name": "Anita Sharma", "specialization": "cardiology",
  "email": "anita@clinic.com", "experience_years": 12 }
```

**Assign doctor to patient**
```json
POST /api/mappings/
{ "patient": 1, "doctor": 1 }
```

> 📮 Import `docs/postman_collection.json` into Postman and run the requests top to bottom.
> The **Login** request stores the token automatically, and the create requests store IDs for later calls.

---

## 🧠 Design Decisions

- **Email as username** – simple login UX while reusing Django's battle-tested `User` model.
- **Data ownership** – patients are filtered by `created_by`, so one user can never read or modify another user's patients (returns 404, not 403, to avoid leaking existence).
- **Doctors are a shared directory** – readable by all authenticated users, writable only by creator (`IsCreatorOrReadOnly`).
- **DB-level uniqueness** – a `UniqueConstraint` on `(patient, doctor)` guarantees no duplicate assignments, with a friendly validation error on top.
- **Secure by default** – `IsAuthenticated` is the global DRF default; only auth endpoints opt out.
- **Secrets in env vars** – nothing sensitive is committed (`.env` is git-ignored).

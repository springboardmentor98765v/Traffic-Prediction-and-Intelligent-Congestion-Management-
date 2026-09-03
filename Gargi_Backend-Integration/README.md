# TrafficVision AI — Backend & Integration

## Overview

This module contains the **Backend & Integration** implementation for the TrafficVision AI project — a Smart Traffic Prediction and Intelligent Congestion Management System.

The backend provides:

* User authentication and authorization
* JWT-based access and refresh tokens
* Role-Based Access Control (RBAC)
* PostgreSQL database integration
* Live traffic monitoring APIs
* Road-wise traffic history
* Traffic density aggregation
* Congestion prediction
* FastAPI REST APIs
* Swagger/OpenAPI documentation
* Automated backend testing

**Team:** Team-3
**Module Owner:** Gargi — Backend & Integration
**Milestone:** Milestone 1

---

## Technology Stack

| Technology      | Purpose                  |
| --------------- | ------------------------ |
| Python          | Backend development      |
| FastAPI         | REST API framework       |
| PostgreSQL      | Relational database      |
| SQLAlchemy      | ORM/database interaction |
| Pydantic        | Data validation          |
| JWT             | Authentication           |
| Uvicorn         | ASGI server              |
| Pytest          | Automated testing        |
| Black           | Code formatting          |
| Flake8          | Code quality             |
| Swagger/OpenAPI | API documentation        |

---

## Project Structure

```text
Gargi_Backend-Integration/
│
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── rbac.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── _init_.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── security.py
│   │   └── _init_.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── seed.py
│   │   └── _init_.py
│   │
│   ├── prediction/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── _init_.py
│   │
│   └── traffic/
│       ├── router.py
│       ├── schemas.py
│       ├── service.py
│       └── _init_.py
│
├── docs/
│   └── Integratioin_doc_m1.md
│
├── tests/
│   └── test_api.py
│
├── .gitignore
└── README.md
```

---

## Backend Architecture

The backend follows a modular architecture:

```text
Client
   │
   ▼
FastAPI Gateway
   │
   ├── Authentication & RBAC
   │
   ├── Traffic Monitoring
   │
   └── Congestion Prediction
   │
   ▼
Service Layer
   │
   ▼
SQLAlchemy ORM
   │
   ▼
PostgreSQL Database
```

The backend is divided into independent modules so that authentication, traffic monitoring, prediction, and database operations can be maintained separately.

---

## Database

The backend uses **PostgreSQL**.

### Main Tables

#### `roles`

Stores available user roles.

```text
id
name
```

Available roles:

* `admin`
* `operator`
* `public`

#### `users`

Stores registered users.

```text
id
name
email
password_hash
role_id
is_active
created_at
```

#### `sessions`

Stores refresh-token session information.

```text
id
user_id
refresh_token
expires_at
created_at
```

#### `roads`

Stores monitored roads.

```text
id
name
```

#### `traffic_records`

Stores traffic observations.

```text
id
road_id
vehicle_count
density
congestion_level
recorded_at
```

---

## Authentication

Authentication is implemented using **JWT access and refresh tokens**.

### Authentication Flow

```text
User
 │
 ├── Register
 │      ↓
 │   Password Hashing
 │      ↓
 │   PostgreSQL
 │
 └── Login
        ↓
     Credentials
        ↓
     JWT Tokens
        ↓
   Access + Refresh Token
```

### Authentication APIs

| Method | Endpoint                | Description                 |
| ------ | ----------------------- | --------------------------- |
| POST   | `/api/v1/auth/register` | Register a new user         |
| POST   | `/api/v1/auth/login`    | Authenticate user           |
| POST   | `/api/v1/auth/refresh`  | Generate a new access token |
| GET    | `/api/v1/auth/me`       | Get current user            |

---

## Role-Based Access Control

Three roles are supported:

| Role       | Access                                  |
| ---------- | --------------------------------------- |
| `admin`    | Full backend access                     |
| `operator` | Traffic operations and monitoring       |
| `public`   | Read-only traffic and prediction access |

Protected endpoints use RBAC middleware to verify the authenticated user's role before allowing access.

---

## Traffic Monitoring APIs

### Live Traffic

```http
GET /api/v1/traffic/live
```

Returns the latest traffic information for monitored roads.

Example response:

```json
[
  {
    "road_id": 1,
    "vehicle_count": 42,
    "density": 0.65,
    "congestion_level": "MEDIUM",
    "updated_at": "2026-09-03T10:30:00Z"
  }
]
```

### Road History

```http
GET /api/v1/traffic/road/{road_id}
```

Returns road information and traffic history.

### Traffic Density

```http
GET /api/v1/traffic/density
```

Returns aggregated traffic-density metrics.

### Add Traffic Record

```http
POST /api/v1/traffic/record
```

This endpoint is restricted to authorized `admin` and `operator` users.

---

## Congestion Prediction

The backend currently provides a heuristic-based congestion prediction service.

```http
GET /api/v1/predict/congestion?road_id={id}
```

Example:

```json
{
  "road_id": 1,
  "predicted_level": "MEDIUM",
  "confidence": 0.72,
  "generated_by": "heuristic-v0"
}
```

### Current Prediction Logic

| Density   | Predicted Level | Confidence |
| --------- | --------------- | ---------- |
| `>= 0.80` | HIGH            | 0.88       |
| `>= 0.50` | MEDIUM          | 0.72       |
| `< 0.50`  | LOW             | 0.60       |

The heuristic implementation provides the initial Milestone 1 prediction layer and can later be replaced or integrated with the AI/ML model developed by the Intelligent Routing team.

---

## Sample Seed Data

The database seed script provides initial roles and road/traffic data.

### Roads

```text
1 — Anna Salai
2 — Mount Road
3 — GST Road
```

### Sample Traffic

```text
Anna Salai  → 42 vehicles → density 0.65 → MEDIUM
Mount Road  → 75 vehicles → density 0.85 → HIGH
GST Road    → 20 vehicles → density 0.30 → LOW
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/springboardmentor98765v/Traffic-Prediction-and-Intelligent-Congestion-Management-.git
```

### 2. Navigate to the Backend

```bash
cd Traffic-Prediction-and-Intelligent-Congestion-Management-/Gargi_Backend-Integration
```

### 3. Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate:

```powershell
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r app/requirements.txt
```

### 5. Configure Environment Variables

Copy the example environment file and configure the local database and JWT settings.

```text
app/.env.example
```

Do **not** commit the actual `.env` file.

---

## PostgreSQL Configuration

Create a PostgreSQL database named:

```text
trafficvision
```

Configure the database connection using:

```text
DATABASE_URL
```

Example format:

```text
postgresql://postgres:<password>@localhost:5432/trafficvision
```

---

## Seed the Database

From the project root:

```bash
python -m app.database.seed
```

This creates the initial roles, roads, and traffic records.

---

## Running the Backend

Start the FastAPI application using:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:

```text
http://127.0.0.1:8000/redoc
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Testing

The backend contains automated API and integration tests using Pytest.

Run:

```bash
pytest -v
```

### Milestone 1 Test Result

```text
15 passed
```

The backend was also checked using:

```bash
python -m black app tests
```

and:

```bash
flake8 app tests
```

Both formatting and static code-quality checks passed.

---

## Security

The backend includes:

* Password hashing
* JWT authentication
* Access-token validation
* Refresh-token validation
* Role-based authorization
* Protected API endpoints
* Environment-based configuration
* `.env` exclusion through `.gitignore`

Secrets and local environment files must never be committed to GitHub.

---

## Milestone 1 Status

### Completed

* [x] FastAPI backend
* [x] PostgreSQL integration
* [x] Database models
* [x] Database seed data
* [x] User registration
* [x] User login
* [x] JWT authentication
* [x] Refresh-token flow
* [x] RBAC
* [x] Traffic monitoring APIs
* [x] Road traffic history
* [x] Traffic density API
* [x] Congestion prediction API
* [x] Swagger/OpenAPI documentation
* [x] Automated tests
* [x] Black formatting
* [x] Flake8 validation
* [x] Backend integration documentation

---

## Milestone 1 Scope Note

Production deployment is **out of scope for Milestone 1**.

The backend is currently prepared for integration with:

* Traffic Monitoring
* AI/ML Intelligent Routing
* Frontend Application Services
* QA and DevOps infrastructure

Future milestones can replace the heuristic prediction service with the trained AI/ML model and integrate additional real-time traffic data sources.

---

## Team Ownership

**Team-3 — Backend & Integration**

**Module Owner:** Gargi

The backend acts as the integration layer between the traffic monitoring, AI/ML prediction, frontend, and QA components of TrafficVision AI.

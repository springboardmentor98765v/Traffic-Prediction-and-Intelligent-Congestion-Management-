# TrafficVision AI — Milestone 2 Backend Handoff

## 1. Purpose

This document provides the setup, architecture, API, testing, and operational information required to continue development of the TrafficVision AI backend after Milestone 2.

The M2 backend is implemented using FastAPI, PostgreSQL, SQLAlchemy, Docker Compose, and a trained machine-learning congestion model.

---

## 2. Project Location

Backend root:

```text
backend/
```

Important directories:

```text
backend/
├── app/
├── ml/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
└── trafficvision_demo.db
```

---

## 3. Application Structure

```text
app/
├── main.py
│
├── auth/
│   ├── dependencies.py
│   ├── rbac.py
│   ├── router.py
│   └── schemas.py
│
├── core/
│   ├── config.py
│   ├── exceptions.py
│   ├── security.py
│   └── rate_limit.py
│
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── seed.py
│   └── generate_traffic.py
│
├── prediction/
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
├── traffic/
│   ├── router.py
│   ├── schemas.py
│   └── service.py
│
└── route/
    ├── maps.py
    ├── ranking.py
    ├── router.py
    ├── schemas.py
    ├── service.py
    ├── storage.py
    └── conditions.py
```

---

## 4. Technology Stack

| Component           | Technology       |
| ------------------- | ---------------- |
| Backend framework   | FastAPI          |
| Server              | Uvicorn          |
| Language            | Python           |
| Database            | PostgreSQL       |
| ORM                 | SQLAlchemy       |
| Authentication      | JWT              |
| Password hashing    | Passlib + bcrypt |
| ML                  | scikit-learn     |
| Model serialization | Joblib           |
| Routing             | OSRM             |
| Map ecosystem       | OpenStreetMap    |
| Testing             | Pytest           |
| Formatting          | Black            |
| Linting             | Flake8           |
| Containerization    | Docker           |
| Orchestration       | Docker Compose   |

---

## 5. Environment Configuration

The local development environment uses a `.env` file.

Example configuration:

```text
APP_NAME=TrafficVision AI Backend
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/trafficvision
JWT_SECRET_KEY=trafficvision-development-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Do not commit production secrets to Git.

The `.env` file should remain excluded from version control.

---

## 6. Running Locally

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Start the FastAPI server:

```powershell
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://localhost:8000
```

---

## 7. Docker Setup

Docker Compose is the recommended method for reproducing the complete M2 backend environment.

Start the services:

```powershell
docker compose up -d --build
```

Check the containers:

```powershell
docker compose ps
```

Expected services:

```text
trafficvision-backend
trafficvision-postgres
```

Stop the services:

```powershell
docker compose down
```

Rebuild after source changes:

```powershell
docker compose down
docker compose up -d --build
```

---

## 8. Docker Services

### Backend

Container:

```text
trafficvision-backend
```

Port:

```text
8000
```

### PostgreSQL

Container:

```text
trafficvision-postgres
```

Port:

```text
5432
```

Inside Docker, the backend connects to PostgreSQL using the service hostname:

```text
db
```

The Docker database URL is:

```text
postgresql://postgres:password@db:5432/trafficvision
```

---

## 9. API Documentation

After starting the backend, Swagger UI is available at:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

ReDoc:

```text
http://localhost:8000/redoc
```

These endpoints should be used during frontend integration and API testing.

---

## 10. API Endpoint Reference

### General

```text
GET /
GET /health
```

### Authentication

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

### Traffic

```text
GET  /api/v1/traffic/history
GET  /api/v1/traffic/aggregate
POST /api/v1/traffic/record
```

### Prediction

```text
GET /api/v1/predict/congestion
GET /api/v1/predict/peak-hours
GET /api/v1/predict/delay
```

### Route Analysis

```text
GET /api/v1/route/optimize
GET /api/v1/route/alternate
GET /api/v1/route/travel-time
GET /api/v1/route/conditions
```

---

## 11. Authentication Workflow

A typical authenticated workflow is:

```text
1. Register or use an existing account
          |
          v
2. Login
          |
          v
3. Receive JWT access token
          |
          v
4. Send token using Authorization header
          |
          v
5. Access protected endpoints
```

Authorization header format:

```text
Authorization: Bearer <access_token>
```

---

## 12. Roles

The application supports:

```text
admin
operator
public
```

Traffic recording is restricted to:

```text
admin
operator
```

Public users cannot create traffic records.

RBAC is implemented through:

```text
app/auth/rbac.py
```

and authentication dependencies.

---

## 13. Traffic Data

The primary traffic record contains:

```text
road_id
vehicle_count
density
congestion_level
recorded_at
```

Example road data currently seeded:

```text
1 — Anna Salai
2 — Mount Road
3 — GST Road
```

Example traffic levels:

```text
LOW
MEDIUM
HIGH
```

---

## 14. Prediction Model

The trained model is located at:

```text
ml/models/congestion_model.joblib
```

The prediction service loads the model and generates congestion predictions using traffic features.

Current model version:

```text
random-forest-v1
```

Prediction responses include:

```text
road_id
predicted_level
confidence
model_version
```

Future model versions should update the `model_version` value so that prediction results remain traceable.

---

## 15. Route Analysis

The Route Analysis module is located at:

```text
app/route/
```

The maps wrapper is:

```text
app/route/maps.py
```

Route scoring is implemented in:

```text
app/route/ranking.py
```

Route orchestration is handled by:

```text
app/route/service.py
```

The API layer is:

```text
app/route/router.py
```

---

## 16. Maps Integration

The backend uses OSRM for routing.

The maps service communicates with the OSRM routing API and converts the returned GeoJSON route geometry into the application's internal route representation.

The external maps provider is intentionally isolated behind:

```text
MapsService
```

This allows another routing provider to be integrated later without changing the Route Analysis API.

---

## 17. Alternate Route Ranking

Alternate routes are ranked using a congestion score based on:

```text
Route duration
Route distance
Traffic density
```

The ranking logic is implemented in:

```text
app/route/ranking.py
```

Future versions can replace the current scoring formula with a model-based ranking system using real-time prediction outputs.

---

## 18. Route Storage

The current route storage mechanism is in-memory.

Implementation:

```text
app/route/storage.py
```

This is suitable for the current development and demonstration scope.

For a production deployment, route information should be persisted in PostgreSQL or another suitable persistent store.

---

## 19. Rate Limiting

The current application-level rate limiter allows:

```text
60 requests
per 60 seconds
per client IP
```

Implementation:

```text
app/core/rate_limit.py
```

The current implementation stores request timestamps in application memory.

For a multi-instance production deployment, this should be replaced with a shared mechanism such as Redis.

---

## 20. Database

Database models are defined in:

```text
app/database/models.py
```

Current entities include:

```text
roles
users
sessions
roads
traffic_records
road_conditions
```

Database connection handling is implemented in:

```text
app/database/connection.py
```

Database initialization is performed through SQLAlchemy metadata.

---

## 21. Testing

The main M2 test file is:

```text
tests/test_api.py
```

Run the local test suite:

```powershell
python -m pytest -vv
```

Run the Docker test suite:

```powershell
docker compose exec backend pytest -vv
```

Final verified result:

```text
23 passed
```

---

## 22. Code Quality Checks

Run Black:

```powershell
python -m black --check app tests
```

Run Flake8:

```powershell
python -m flake8 app tests
```

Expected result:

```text
Black: PASS
Flake8: PASS
```

---

## 23. Final Docker QA

The final Docker verification completed successfully.

Result:

```text
23 passed, 3 warnings
```

The remaining warnings are from third-party dependencies:

```text
Starlette/httpx
AnyIO
Passlib
```

No application-level datetime deprecation warnings remain.

These warnings do not currently prevent the backend from running or the test suite from passing.

---

## 24. Important Development Rule

Before changing backend functionality:

```text
1. Run existing tests.
2. Make the required change.
3. Run pytest again.
4. Run Black.
5. Run Flake8.
6. Rebuild Docker if Docker-related files changed.
7. Run Docker pytest.
```

The expected final state is always:

```text
23 passed
Black PASS
Flake8 PASS
Docker PASS
```

---

## 25. Debugging Checklist

### Backend does not start

Check:

```powershell
docker compose ps
```

Then:

```powershell
docker compose logs backend
```

### Database connection failure

Check:

```powershell
docker compose logs db
```

Ensure PostgreSQL is running.

### Backend container cannot import `app`

The Dockerfile should contain:

```dockerfile
WORKDIR /app
ENV PYTHONPATH=/app
```

### Tests fail after source changes

Run:

```powershell
python -m pytest -vv
```

before rebuilding Docker.

### Docker is using stale code

Run:

```powershell
docker compose down
docker compose up -d --build
```

---

## 26. M3 Recommended Next Steps

The following improvements are recommended for the next milestone.

### 26.1 Persistent Route Storage

Replace the in-memory route storage with PostgreSQL persistence.

Current:

```text
app/route/storage.py
```

Future:

```text
PostgreSQL route table
```

---

### 26.2 Redis-Based Rate Limiting

Replace the in-memory rate limiter with Redis to support multiple backend instances.

Current:

```text
app/core/rate_limit.py
```

Future architecture:

```text
FastAPI
   |
   v
Redis Rate Limiter
   |
   v
Backend Services
```

---

### 26.3 Advanced Congestion-Aware Routing

Use the trained prediction model directly in route ranking.

Future flow:

```text
Route alternatives
       |
       v
Traffic features
       |
       v
Prediction service
       |
       v
Congestion prediction
       |
       v
Route ranking
       |
       v
Recommended route
```

---

### 26.4 Production Configuration

Future production work should include:

* Secure JWT secrets.
* Environment-specific configuration.
* HTTPS.
* Production database credentials.
* Database migrations.
* Centralized logging.
* Monitoring.
* Health checks.
* Error tracking.
* Container orchestration.

---

### 26.5 Database Migrations

Introduce a migration framework such as Alembic before making significant production schema changes.

---

### 26.6 Dependency Maintenance

The current test environment reports dependency deprecation warnings related to:

* Starlette/httpx.
* AnyIO.
* Passlib.

These should be addressed during a controlled dependency upgrade rather than during the current M2 code freeze.

---

## 27. Code Freeze Status

M2 implementation and QA are complete.

Final status:

```text
Backend implementation     COMPLETE
API integration            COMPLETE
Prediction integration     COMPLETE
Route Analysis             COMPLETE
RBAC                       COMPLETE
Rate limiting              COMPLETE
Docker integration         COMPLETE
Automated testing          COMPLETE
Code quality checks        COMPLETE
Docker QA                  COMPLETE
Documentation              COMPLETE
Code freeze                READY
```

No further functional changes should be introduced into the M2 branch unless a critical defect is discovered.

---

## 28. Handoff Summary

The M2 backend is ready for handoff.

The next development team or milestone should begin from the current tested state and preserve the existing API contracts wherever possible.

The baseline verification standard for future changes is:

```text
23/23 tests passing
Black passing
Flake8 passing
Docker build successful
Docker test suite passing
```

This establishes the M2 backend as the stable baseline for future TrafficVision AI development.

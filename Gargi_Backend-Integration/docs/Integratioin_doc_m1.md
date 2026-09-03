# TrafficVision AI

## Milestone 1 — Backend & Integration Summary

**Role:** Intern 1 — Team Lead / Backend & Integration
**Milestone:** Milestone 1
**Project:** Traffic Prediction and Intelligent Congestion Management System

---

## 1. Overview

TrafficVision AI is a smart traffic management backend designed to provide traffic monitoring, congestion prediction, authentication, role-based access control, and integration-ready APIs for the frontend and other system components.

Milestone 1 establishes the backend foundation required for authentication, traffic monitoring, congestion prediction, API integration, testing, and future expansion.

The backend is implemented using:

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT authentication
* Pydantic
* Pytest
* Black
* Flake8

---

## 2. Backend Architecture

The Milestone 1 backend follows a modular FastAPI architecture.

```text
                    ┌──────────────────────┐
                    │      Frontend        │
                    └──────────┬───────────┘
                               │
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │     /api/v1          │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      ┌────────────┐    ┌────────────┐    ┌────────────┐
      │    Auth    │    │   Traffic  │    │ Prediction │
      │   Module   │    │   Module   │    │   Module   │
      └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │      SQLAlchemy      │
                    │     ORM / Services   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     PostgreSQL       │
                    │       Database       │
                    └──────────────────────┘
```

The `/api/v1` API structure acts as the integration gateway for Milestone 1. Authentication, traffic monitoring, and prediction functionality are exposed through modular routers.

---

## 3. Project Structure

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── auth/
│   │   ├── dependencies.py
│   │   ├── rbac.py
│   │   ├── router.py
│   │   └── schemas.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── seed.py
│   │
│   ├── prediction/
│   │   ├── router.py
│   │   ├── schemas.py
│   │   └── service.py
│   │
│   └── traffic/
│       ├── router.py
│       ├── schemas.py
│       └── service.py
│
├── tests/
│   └── test_api.py
│
├── docs/
│   └── BACKEND_INTEGRATION_SUMMARY_M1.md
│
├── requirements.txt
└── .env.example
```

---

## 4. Database Architecture

PostgreSQL is used as the primary relational database.

The Milestone 1 schema contains the following tables:

### Roles

Stores supported user roles.

```text
roles
-----
id
name
```

Supported roles:

* admin
* operator
* public

### Users

Stores authenticated application users.

```text
users
-----
id
name
email
password_hash
role_id
is_active
created_at
```

Each user is associated with a role.

### Sessions

Stores refresh-token session information.

```text
sessions
--------
id
user_id
refresh_token
expires_at
created_at
```

The table is included in the Milestone 1 database schema for session management and future token persistence.

### Roads

Stores monitored roads.

```text
roads
-----
id
name
```

### Traffic Records

Stores traffic observations.

```text
traffic_records
---------------
id
road_id
vehicle_count
density
congestion_level
recorded_at
```

The traffic record is associated with a road through a foreign key.

---

## 5. Authentication

Authentication is implemented using JWT tokens.

The login process generates:

* Access token
* Refresh token
* User role

The access token is used to authenticate protected API requests.

The refresh token is used to generate a new access token after the previous access token expires.

JWT configuration includes:

```text
Algorithm: HS256
Access token expiry: 30 minutes
Refresh token expiry: 7 days
```

Passwords are stored as password hashes rather than plaintext passwords.

---

## 6. Authentication APIs

### Register

```http
POST /api/v1/auth/register
```

Creates a new user.

Response:

```json
{
    "user_id": 1
}
```

---

### Login

```http
POST /api/v1/auth/login
```

Authenticates a user.

Response:

```json
{
    "access_token": "...",
    "refresh_token": "...",
    "role": "operator"
}
```

---

### Refresh

```http
POST /api/v1/auth/refresh
```

Generates a new access token using a valid refresh token.

Response:

```json
{
    "access_token": "..."
}
```

---

### Current User

```http
GET /api/v1/auth/me
```

Returns the authenticated user's information.

Response:

```json
{
    "user_id": 2,
    "name": "Operator User",
    "role": "operator"
}
```

---

## 7. Role-Based Access Control

Role-based access control is implemented using FastAPI dependencies.

Supported roles:

```text
admin
operator
public
```

Protected endpoints verify the JWT access token before processing requests.

Role restrictions include:

```text
Public:
- Read traffic information
- Request congestion predictions

Operator:
- Read traffic information
- Request congestion predictions
- Create traffic records

Admin:
- Operator permissions
- Administrative access
```

Unauthorized requests receive HTTP 401.

Authenticated users without sufficient permissions receive HTTP 403.

---

## 8. Traffic Monitoring APIs

### Live Traffic

```http
GET /api/v1/traffic/live
```

Returns the latest traffic record for each monitored road.

Example:

```json
[
    {
        "road_id": 1,
        "vehicle_count": 42,
        "density": 0.65,
        "congestion_level": "MEDIUM",
        "updated_at": "..."
    }
]
```

---

### Road Traffic

```http
GET /api/v1/traffic/road/{road_id}
```

Returns road information, current congestion level, and traffic history.

---

### Traffic Density

```http
GET /api/v1/traffic/density
```

Returns the latest density and congestion information for monitored roads.

---

### Traffic Record

```http
POST /api/v1/traffic/record
```

Allows authorized users to create a traffic record.

This endpoint is restricted to:

* admin
* operator

---

## 9. Prediction Service

Milestone 1 uses a deterministic heuristic prediction service.

The prediction is based on the latest traffic density.

```text
Density >= 0.80
        ↓
      HIGH
   confidence 0.88

Density >= 0.50
        ↓
     MEDIUM
   confidence 0.72

Density < 0.50
        ↓
       LOW
   confidence 0.60
```

The prediction identifies itself using:

```text
generated_by = "heuristic-v0"
```

This is intentionally a baseline implementation for Milestone 1. A machine-learning prediction model can replace or extend the heuristic service in a future milestone.

---

## 10. Prediction API

```http
GET /api/v1/predict/congestion?road_id={id}
```

Example response:

```json
{
    "road_id": 2,
    "predicted_level": "HIGH",
    "confidence": 0.88,
    "generated_by": "heuristic-v0"
}
```

If traffic data does not exist for the requested road, the API returns HTTP 404.

---

## 11. Seed Data

The database contains initial development data.

### Roles

```text
admin
operator
public
```

### Roads

```text
1 - Anna Salai
2 - Mount Road
3 - GST Road
```

### Traffic Data

```text
Anna Salai
vehicle_count: 42
density: 0.65
congestion: MEDIUM

Mount Road
vehicle_count: 75
density: 0.85
congestion: HIGH

GST Road
vehicle_count: 20
density: 0.30
congestion: LOW
```

---

## 12. Testing

Backend API integration tests are implemented using Pytest and FastAPI TestClient.

The final test suite contains:

```text
15 tests
15 passed
0 failed
```

The tests cover:

* Root endpoint
* Health endpoint
* Authentication requirements
* Operator login
* Current-user endpoint
* Live traffic endpoint
* Road traffic endpoint
* Traffic density endpoint
* Prediction endpoint
* Invalid prediction road
* OpenAPI endpoint coverage

Final test result:

```text
15 passed
```

---

## 13. Code Quality

The backend was checked using:

### Black

```text
python -m black app tests
```

Result:

```text
All files formatted successfully.
```

### Flake8

```text
python -m flake8 app tests
```

Result:

```text
No linting errors.
```

---

## 14. API Documentation

FastAPI automatically generates OpenAPI documentation.

The interactive Swagger UI is available at:

```text
/docs
```

The OpenAPI specification is available at:

```text
/openapi.json
```

The documented API includes authentication, traffic monitoring, and congestion prediction endpoints.

---

## 15. Milestone 1 Scope

The following functionality has been completed:

* FastAPI backend foundation
* PostgreSQL integration
* User and role management
* JWT authentication
* Refresh-token flow
* Role-based access control
* Traffic monitoring APIs
* Traffic history APIs
* Traffic density APIs
* Congestion prediction API
* Heuristic prediction service
* Backend integration
* API testing
* Swagger/OpenAPI documentation
* Code formatting
* Static linting

---

## 16. Known Milestone 1 Limitations

### Refresh Token Persistence

The `sessions` database table exists, but the current refresh endpoint validates the refresh JWT directly rather than persisting and validating every issued refresh token against the sessions table.

This can be strengthened in a future iteration by storing, rotating, revoking, and validating refresh tokens through the session table.

### Gateway Architecture

For Milestone 1, the FastAPI application provides the unified `/api/v1` API gateway and integrates the authentication, traffic, and prediction modules.

A separate reverse-proxy or microservice gateway is not required for the current milestone scope.

### Prediction

The prediction service currently uses a deterministic heuristic (`heuristic-v0`) rather than a trained machine-learning model.

---

## 17. Integration Status

```text
Authentication              COMPLETE
JWT Authentication          COMPLETE
RBAC                        COMPLETE
PostgreSQL Integration      COMPLETE
Traffic Monitoring          COMPLETE
Traffic History             COMPLETE
Traffic Density             COMPLETE
Prediction API              COMPLETE
Backend Integration         COMPLETE
Automated Tests             COMPLETE
Swagger/OpenAPI             COMPLETE
Black Formatting            COMPLETE
Flake8 Linting              COMPLETE FROM THIS DOCUMENT
```

---

## 18. Intern 1 Sign-off

The Milestone 1 Backend & Integration implementation is functionally complete within the defined scope.

The backend is ready for:

* Frontend integration
* QA verification
* Milestone 1 demonstration
* Future ML model integration
* Future production hardening

Further backend changes should be limited to critical bug fixes after code freeze.

**Intern 1 — Backend & Integration:** Gargi Mohajan

**Milestone:** M1

**Status:** Ready for Code Freeze

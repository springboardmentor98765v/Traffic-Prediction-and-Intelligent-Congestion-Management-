# Backend Architecture & Integration Summary — Milestone 1

## Service Overview

The Backend follows an **API Gateway pattern** — a single FastAPI application that routes requests to three logical service modules:

| Service | Prefix | Description |
|---------|--------|-------------|
| Authentication | `/api/v1/auth` | User registration, login, JWT token management, RBAC |
| Traffic Monitoring | `/api/v1/traffic` | Live traffic data, road status, congestion metrics |
| AI Engine (Stub) | `/api/v1/predict` | Heuristic congestion prediction placeholder |

## Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL via SQLAlchemy ORM
- **Cache**: Redis (ready, not yet wired in Milestone 1 stubs)
- **Auth**: JWT via python-jose + bcrypt via passlib
- **Containerization**: Docker

## Project Structure

```
Backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py            # Settings via pydantic-settings
│   ├── database/
│   │   └── connection.py    # SQLAlchemy engine, session, Base
│   ├── models/
│   │   └── user.py          # User, RefreshToken, UserRole enum
│   ├── schemas/
│   │   └── auth.py          # Pydantic request/response models
│   ├── routers/
│   │   ├── auth.py          # /api/v1/auth/* endpoints
│   │   ├── traffic.py       # /api/v1/traffic/* stub endpoints
│   │   └── prediction.py    # /api/v1/predict/* stub endpoints
│   ├── middleware/
│   │   └── auth_middleware.py  # JWT verification + role-based access
│   └── services/
│       └── jwt_service.py   # Token creation, verification, password hashing
├── migrations/
│   └── 001_create_users_tables.sql
├── Dockerfile
├── requirements.txt
├── run.py                   # Local dev entry point
└── .env.example
```

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Register a new user |
| POST | `/login` | No | Login, receive access + refresh tokens |
| POST | `/refresh` | No | Exchange refresh token for new access token |
| GET | `/me` | Bearer | Get current user profile |
| GET | `/users` | Admin | List all users (RBAC: admin only) |

### Traffic Monitoring (`/api/v1/traffic`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/live` | Bearer | Live traffic for all road segments |
| GET | `/road/{road_id}` | Bearer | Traffic detail + history for one road |
| GET | `/density` | Bearer | Aggregated density metrics |

### AI Engine - Prediction (`/api/v1/predict`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/congestion?road_id={id}` | Bearer | Heuristic congestion prediction |

## RBAC Model

Three roles with increasing access:

| Role | Access |
|------|--------|
| `public` | Read traffic data, view predictions |
| `operator` | Same as public (extensible in M2) |
| `admin` | Full access including user management |

## Database Schema (Milestone 1)

### Users Table
- `id` (UUID, PK)
- `name` (VARCHAR 100)
- `email` (VARCHAR 255, unique, indexed)
- `password_hash` (VARCHAR 255)
- `role` (ENUM: admin, operator, public)
- `created_at`, `updated_at` (TIMESTAMP)

### Refresh Tokens Table
- `id` (UUID, PK)
- `user_id` (UUID, FK → users.id, CASCADE)
- `token` (VARCHAR 500, unique, indexed)
- `expires_at` (TIMESTAMP)
- `created_at` (TIMESTAMP)

## Integration Points

- **Intern 2 (Traffic Monitoring)**: Traffic stub endpoints consume the same data schema defined in `Komal_Data-Engineering-Traffic-Monitoring/traffic_schema.md`. Will be replaced with real ingestion pipeline in M2.
- **Intern 3 (AI/ML)**: Prediction stub uses heuristic logic. Real ML model integration planned for M2.
- **Intern 4 (Frontend)**: Consumes all API endpoints via HTTP. CORS configured for local dev.
- **Intern 5 (DevOps)**: Dockerfile provided. Backend container integrates into `docker-compose.dev.yml`.

## How to Run

### Local Development
```bash
cd Backend
cp .env.example .env
pip install -r requirements.txt
python run.py
```

### Docker
```bash
cd Backend
docker build -t trafficvision-backend .
docker run -p 8000:8000 --env-file .env trafficvision-backend
```

### Full Stack (via docker-compose)
```bash
# From srinath-devops/docker-compose.dev.yml
docker compose -f docker-compose.dev.yml up
```

## Milestone 1 Status

| Deliverable | Status |
|-------------|--------|
| FastAPI app skeleton | Done |
| Auth service (register, login, refresh, me) | Done |
| RBAC middleware + admin route | Done |
| API Gateway routing | Done |
| Traffic Monitoring stub | Done |
| Prediction stub (heuristic) | Done |
| Swagger/OpenAPI docs | Done |
| Dockerfile | Done |
| run.py entry point | Done |
| DB migration script | Done |

## Milestone 2 Handoff Notes

- Replace traffic stubs with real ingestion pipeline from Intern 2
- Replace prediction heuristic with trained ML model from Intern 3
- Add Redis caching layer for live traffic reads
- Add MongoDB/Data Lake for historical data storage
- Expand RBAC for new service endpoints

# Backend Architecture & Integration Summary — Milestone 3
## TrafficVision AI: Smart Traffic Prediction & Congestion Management System

---

## Service Overview

The Backend follows an **API Gateway pattern** — a unified FastAPI application that routes requests to seven logical service modules:

| Service | Prefix | Owner | Description |
|---------|--------|-------|-------------|
| **Alert Service** (NEW) | `/api/v1/alerts` | Intern 1 | Congestion, accident, closure, delay alerts; in-app notification workflows; REST polling & WebSocket delivery; RBAC scoping |
| **Analytics Service** (NEW) | `/api/v1/analytics` | Intern 2 / Gateway | Traffic trend analysis (daily/weekly), 2D congestion heatmaps, and downloadable historical reports (CSV/JSON) |
| **AI Engine - Insights** (NEW) | `/api/v1/ai` | Intern 3 / Gateway | Traffic anomaly detection (accident proxy), auto-alert feeds, and AI-powered recommendations |
| **Route Analysis** | `/api/v1/route` | Backend | Route optimization, congestion-aware alternate routes, travel-time estimation, and road-condition tracking |
| **AI Engine - Prediction** | `/api/v1/predict` | Backend | Real trained ML model (`model-v1`), peak-hour forecasting, delay estimation, and prediction reports |
| **Traffic Monitoring** | `/api/v1/traffic` | Backend | Live telemetry, historical time-series queries, aggregations, and road status |
| **Authentication** | `/api/v1/auth` | Backend | User registration, login, JWT token lifecycle, and role-based access control (RBAC) |

---

## Tech Stack (Milestone 3)

- **Framework**: FastAPI (Python 3.13)
- **Database**: PostgreSQL / SQLite via SQLAlchemy ORM (relational models for Users, RefreshTokens, RoadConditions, Alerts, AlertReads)
- **Cache**: Redis / In-Memory cache fallback with TTL expiration
- **Auth**: JWT via `python-jose` + bcrypt password hashing via `passlib`
- **Machine Learning**: `scikit-learn` (Random Forest Classifier, `model-v1`), `pandas`, `numpy`, `joblib`
- **Mapping & Routing**: OpenStreetMap / OSRM API wrapper with local road-network topology fallback
- **Real-Time Notification Delivery**: Short-interval REST polling (`/api/v1/alerts/poll`) + FastAPI WebSocket (`/api/v1/alerts/ws`) stretch goal
- **Rate Limiting & Anti-Noise**: Sliding-window rate limiting middleware with standard `X-RateLimit-*` headers + Alert deduplication window
- **Testing**: `pytest`, `httpx` (49 automated unit and integration tests passing with 0 failures)

---

## Project Structure

```
Backend/
├── app/
│   ├── main.py                     # FastAPI Gateway, CORS, rate-limit middleware, router registration
│   ├── config.py                   # Settings via pydantic-settings
│   ├── database/
│   │   └── connection.py           # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── __init__.py             # Model exports (User, RoadCondition, Alert, AlertRead)
│   │   ├── user.py                 # User, RefreshToken, UserRole enum
│   │   ├── road_condition.py       # RoadCondition, RoadStatus enum
│   │   └── alert.py                # Alert, AlertRead, AlertType, AlertSeverity enums (M3)
│   ├── schemas/
│   │   ├── __init__.py             # Schema exports
│   │   ├── auth.py                 # Auth request/response schemas
│   │   ├── route.py                # Route optimization, alternates, travel-time schemas
│   │   ├── prediction.py           # Prediction model-v1, peak-hours, delay schemas
│   │   ├── traffic.py              # Historical time-series and aggregate schemas
│   │   ├── alert.py                # Alert schemas: create, response, read, poll, triggers (M3)
│   │   ├── analytics.py            # Analytics schemas: trends, heatmap, historical reports (M3)
│   │   └── ai.py                   # AI schemas: anomalies, recommendations (M3)
│   ├── routers/
│   │   ├── __init__.py             # Router exports
│   │   ├── auth.py                 # /api/v1/auth/* endpoints
│   │   ├── traffic.py              # /api/v1/traffic/* endpoints (live, history, aggregate, conditions)
│   │   ├── prediction.py           # /api/v1/predict/* endpoints (model-v1, peak-hours, delay, report)
│   │   ├── route.py                # /api/v1/route/* endpoints (optimize, alternate, travel-time, conditions)
│   │   ├── alerts.py               # /api/v1/alerts/* endpoints (my, read, active, poll, evaluate-triggers, ws) (M3)
│   │   ├── analytics.py            # /api/v1/analytics/* endpoints (trends, heatmap, reports) (M3)
│   │   └── ai.py                   # /api/v1/ai/* endpoints (anomalies, recommendations) (M3)
│   ├── middleware/
│   │   ├── auth_middleware.py      # JWT verification & role-based access control
│   │   └── rate_limit.py           # Sliding-window rate limiter with headers & 429
│   ├── services/
│   │   ├── jwt_service.py          # Token creation, verification, password hashing
│   │   ├── traffic_service.py      # Live readings, history queries, aggregations
│   │   ├── maps_service.py         # OpenStreetMap/OSRM wrapper + GPS graph
│   │   ├── ml_prediction_service.py# Trained scikit-learn model-v1, forecasting, reports
│   │   ├── prediction_service.py   # Heuristic backward compatibility fallback
│   │   ├── route_service.py        # Congestion-aware route evaluation & ranking
│   │   ├── road_condition_service.py# Road hazards, construction, closures
│   │   ├── alert_service.py        # Alert creation, deduplication, RBAC scoping, polling, WS (M3)
│   │   ├── analytics_service.py    # Trend analysis, heatmap matrix, CSV/JSON report exports (M3)
│   │   └── ai_insights_service.py  # Anomaly detection, accident alerts, AI recommendations (M3)
│   └── data/
│       ├── processed_traffic.csv   # Multi-week training & telemetry dataset
│       └── congestion_model.joblib # Serialized Random Forest ML model artifact
├── migrations/
│   ├── 001_create_users_tables.sql
│   ├── 002_create_m2_tables.sql
│   └── 003_create_m3_alerts_tables.sql # M3 alerts and alert_reads tables
├── tests/
│   ├── conftest.py                 # Test fixtures (rate limit cache clearing)
│   ├── test_auth.py                # Auth & RBAC test suite (M1 regression)
│   ├── test_traffic.py             # Traffic monitoring test suite (M1 regression)
│   ├── test_prediction.py          # Prediction baseline test suite (M1 regression)
│   ├── test_route.py               # Route optimization & alternates test suite (M2)
│   ├── test_prediction_m2.py       # Model-v1, peak-hours, delay, report test suite (M2)
│   ├── test_traffic_m2.py          # Historical & aggregated traffic test suite (M2)
│   ├── test_rate_limit.py          # Rate limiting & headers test suite (M2)
│   ├── test_alerts_m3.py           # Alert Service, deduplication, RBAC, polling, triggers (M3)
│   ├── test_analytics_m3.py        # Trends, heatmap, historical CSV/JSON reports (M3)
│   └── test_ai_insights_m3.py      # Anomaly detection & AI recommendations (M3)
├── Dockerfile
├── requirements.txt
├── run.py
└── .env.example
```

---

## API Endpoints Reference — Milestone 3

### 1. Alert Service & Notifications (`/api/v1/alerts`)

| Method | Path | Auth / Role | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/v1/alerts` | Internal / System | Ingests alert events with anti-noise deduplication (FR-01, FR-02, FR-03) |
| `GET` | `/api/v1/alerts/my` | Optional / Role-Scoped | In-app notifications scoped by role (Admin/Operator see all; Public sees safety alerts) (FR-04) |
| `POST` | `/api/v1/alerts/{alert_id}/read` | Optional / Any | Marks an alert as read for the user, recording in `alert_reads` |
| `GET` | `/api/v1/alerts/active` | Public / Operator | List of currently active alerts for dashboard display |
| `GET` | `/api/v1/alerts/poll?since={iso}` | Optional / Role-Scoped | Short-interval REST polling endpoint with unread count and active count |
| `POST` | `/api/v1/alerts/evaluate-triggers` | Internal / Operator | Evaluates all active threshold feeds, closures, and anomalies |
| `WS` | `/api/v1/alerts/ws` | Public | Real-time WebSocket notification broadcast stream (stretch goal) |

### 2. Analytics Service (`/api/v1/analytics`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/analytics/trends?road_id={id}&range=day\|week` | Public | Hourly/daily traffic trends, average congestion, speed, and density (FR-05) |
| `GET` | `/api/v1/analytics/heatmap?range=day\|week` | Public | 2D congestion intensity matrix across roads and time buckets (FR-06) |
| `GET` | `/api/v1/analytics/reports?range={range}&format=csv\|json` | Public | Downloadable historical traffic reports with CSV header attachment (FR-07) |

### 3. AI Engine - Insights & Recommendations (`/api/v1/ai`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/ai/anomalies?auto_alert=true\|false` | Public | Flags unexpected traffic patterns deviating from ML expectations (FR-02) |
| `GET` | `/api/v1/ai/recommendations?road_id={id}` | Public | Explainable recommendations for departure windows & alternate routes (FR-08) |

### 4. Milestone 1 & 2 Core Endpoints (Zero Regression Maintained)

- **Route Analysis**: `/api/v1/route/optimize`, `/alternate`, `/travel-time`, `/conditions`
- **Prediction**: `/api/v1/predict/congestion`, `/peak-hours`, `/delay`, `/report`, `/live`
- **Traffic Monitoring**: `/api/v1/traffic/live`, `/road/{road_id}`, `/density`, `/history`, `/aggregate`, `/road-condition/{road_id}`
- **Authentication**: `/api/v1/auth/register`, `/login`, `/refresh`, `/me`, `/users`

---

## Role-Based Access Control (RBAC) in Milestone 3

Alert visibility is strictly scoped by role:
- **Admin**: Has visibility into all alerts, system logs, operational maintenance notices, and public alerts.
- **Operator**: Has visibility into monitoring breaches, road condition overrides, and all traffic alerts.
- **Public**: Has visibility into public safety alerts: accidents (`accident`), road closures (`closure`), delay warnings (`delay`), and severe congestion (`congestion`). Internal operational alerts are filtered out.

---

## Anti-Noise & Deduplication Strategy

To prevent alert fatigue and notification spam (addressing SRS Risk Section 15):
- The Alert Service maintains a 15-minute sliding deduplication window per `(road_id, type)`.
- If a new threshold breach or anomaly arrives for the same road and alert type while an active alert exists, the existing alert's timestamp, severity, and message are updated rather than creating duplicate notifications.

---

## Test Verification Summary

- **Total Tests**: 49
- **Passing**: 49 (100%)
- **Failing**: 0
- **Regression**: 0 issues across all M1 & M2 test suites.

---

## Milestone 4 Handoff Notes (Deployment Readiness Preparation)

- **Production Database**: PostgreSQL schemas verified via `migrations/001`, `002`, `003`.
- **Environment Variables**: Configure `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and `RATE_LIMIT_ENABLED`.
- **Containerization**: `docker-compose.dev.yml` contains backend, PostgreSQL, and Redis containers. Production manifest ready for staging in Milestone 4.

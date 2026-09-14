# Backend Architecture & Integration Summary — Milestone 2

## Service Overview

The Backend follows an **API Gateway pattern** — a unified FastAPI application that routes requests to four logical service modules:

| Service | Prefix | Description |
|---------|--------|-------------|
| Route Analysis | `/api/v1/route` | Route optimization, congestion-aware alternate routes, travel-time estimation, and road-condition tracking |
| AI Engine - Prediction | `/api/v1/predict` | Real trained ML model (`model-v1`), peak-hour forecasting, delay estimation, and prediction reports |
| Traffic Monitoring | `/api/v1/traffic` | Live telemetry, historical time-series queries, aggregations, and road status |
| Authentication | `/api/v1/auth` | User registration, login, JWT token lifecycle, and role-based access control (RBAC) |

---

## Tech Stack (Milestone 2)

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL / SQLite via SQLAlchemy ORM
- **Cache**: Redis / In-Memory cache fallback with TTL expiration
- **Auth**: JWT via `python-jose` + bcrypt hashing via `passlib`
- **Machine Learning**: `scikit-learn` (Random Forest Classifier, `model-v1`), `pandas`, `numpy`, `joblib`
- **Mapping & Routing**: OpenStreetMap / OSRM API wrapper with local Bangalore road-network topology fallback
- **Rate Limiting**: Sliding-window rate limiting middleware with standard `X-RateLimit-*` headers and HTTP 429 enforcement
- **Testing**: `pytest`, `httpx`

---

## Project Structure

```
Backend/
├── app/
│   ├── main.py                  # FastAPI app, CORS, rate-limit middleware, router registration
│   ├── config.py                # Settings via pydantic-settings
│   ├── database/
│   │   └── connection.py        # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── __init__.py          # Model exports
│   │   ├── user.py              # User, RefreshToken, UserRole enum
│   │   └── road_condition.py    # RoadCondition, RoadStatus enum
│   ├── schemas/
│   │   ├── __init__.py          # Schema exports
│   │   ├── auth.py              # Auth request/response schemas
│   │   ├── route.py             # Route optimization, alternates, travel-time schemas
│   │   ├── prediction.py        # Prediction model-v1, peak-hours, delay schemas
│   │   └── traffic.py           # Historical time-series and aggregate schemas
│   ├── routers/
│   │   ├── auth.py              # /api/v1/auth/* endpoints
│   │   ├── traffic.py           # /api/v1/traffic/* endpoints (live, history, aggregate, conditions)
│   │   ├── prediction.py        # /api/v1/predict/* endpoints (model-v1, peak-hours, delay, report)
│   │   └── route.py             # /api/v1/route/* endpoints (optimize, alternate, travel-time, conditions)
│   ├── middleware/
│   │   ├── auth_middleware.py   # JWT verification & role-based access control
│   │   └── rate_limit.py        # Sliding-window rate limiter with headers & 429
│   ├── services/
│   │   ├── jwt_service.py       # Token creation, verification, password hashing
│   │   ├── traffic_service.py   # Live readings, history queries, aggregations
│   │   ├── maps_service.py      # OpenStreetMap/OSRM wrapper + Bangalore GPS graph
│   │   ├── ml_prediction_service.py # Trained scikit-learn model-v1, forecasting, reports
│   │   ├── prediction_service.py # Heuristic backward compatibility fallback
│   │   ├── route_service.py     # Congestion-aware route evaluation & ranking
│   │   └── road_condition_service.py # Road hazards, construction, closures
│   └── data/
│       ├── processed_traffic.csv # Multi-week training dataset
│       └── congestion_model.joblib # Serialized ML model artifact
├── migrations/
│   ├── 001_create_users_tables.sql
│   └── 002_create_m2_tables.sql
├── tests/
│   ├── test_auth.py             # Auth & RBAC test suite (M1 regression)
│   ├── test_traffic.py          # Traffic monitoring test suite (M1 regression)
│   ├── test_prediction.py       # Prediction baseline test suite
│   ├── test_route.py            # Route optimization & alternates test suite (M2)
│   ├── test_prediction_m2.py    # Model-v1, peak-hours, delay, report test suite (M2)
│   ├── test_traffic_m2.py       # Historical & aggregated traffic test suite (M2)
│   └── test_rate_limit.py       # Rate limiting & headers test suite (M2)
├── Dockerfile
├── requirements.txt
├── run.py                       # Local dev entry point
└── .env.example
```

---

## API Endpoints Reference

### 1. Route Analysis Service (`/api/v1/route`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/optimize?origin={}&destination={}` | Optional | Optimal route based on map geometry, density, and ML congestion score |
| GET | `/alternate?origin={}&destination={}` | Optional | Alternate candidate routes ranked by predicted congestion and delay |
| GET | `/travel-time?route_id={id}` | Optional | Estimated travel time, free-flow time, and delay (`based_on: "live+predicted"`) |
| GET | `/conditions?road_id={id}` | Optional | Status (`OPEN`, `CONSTRUCTION`, `CLOSED`, `HAZARD`) and hazard notes |
| POST | `/conditions` | Operator/Admin | Update road condition status, construction, or hazard flags |

### 2. AI Engine - Prediction (`/api/v1/predict`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/congestion?road_id={id}` | Optional | Predict congestion level using trained ML model (`model-v1`) |
| GET | `/peak-hours?road_id={id}` | Optional | Forecast peak-hour congestion windows (start, end, severity) |
| GET | `/delay?road_id={id}` | Optional | Estimated delay in minutes based on free-flow vs congested speed |
| GET | `/report?road_id={id}&format=json\|csv` | Optional | Downloadable 24-hour predictive forecast report (FR-09) |
| GET | `/live` | Optional | Live model-v1 predictions for all monitored corridors |

### 3. Traffic Monitoring (`/api/v1/traffic`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/live` | Optional | Live traffic status and density for all road segments |
| GET | `/road/{road_id}` | Optional | Detailed current and hourly traffic for a specific road |
| GET | `/density` | Optional | Aggregated city-wide density KPIs and congested road count |
| GET | `/history?road_id={}&start={}&end={}` | Optional | Query historical time-series traffic records (FR-01) |
| GET | `/aggregate?road_id={}&granularity=hour\|day` | Optional | Hourly and daily rolled-up statistics (FR-01) |
| GET | `/road-condition/{road_id}` | Optional | Road condition flag lookup for a specific corridor |

### 4. Authentication (`/api/v1/auth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Register a new user |
| POST | `/login` | No | Authenticate and receive JWT access + refresh tokens |
| POST | `/refresh` | No | Exchange refresh token for new access token |
| GET | `/me` | Bearer | Retrieve current user profile |
| GET | `/users` | Admin | List all registered users (RBAC: admin only) |

---

## Rate Limiting & Security

- **Tiers**:
  - `public` / unauthenticated: 60 requests / minute
  - `operator`: 120 requests / minute
  - `admin`: 300 requests / minute
- **Headers Returned**:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Seconds until window reset
- **Status Code 429**: Returned when limit is exceeded.

---

## Milestone 2 Deliverables Status

| Deliverable | Status |
|-------------|--------|
| Maps/Traffic API wrapper (`maps_service.py`) | Done |
| Route Analysis Service (`route_service.py`, `routers/route.py`) | Done |
| Real trained prediction model (`ml_prediction_service.py`, `model-v1`) | Done |
| Peak-hour forecasting & delay estimation | Done |
| Downloadable prediction reports (`/predict/report`) | Done |
| Historical traffic & aggregations (`/traffic/history`, `/traffic/aggregate`) | Done |
| Road condition monitoring & management | Done |
| Rate limiting middleware & extended RBAC | Done |
| Local unit & integration test suites | Done |
| Zero-regression on Milestone 1 features | Verified |

---

## Milestone 3 Handoff Notes

- **Dynamic Congestion Re-routing**: Integrate real-time incident streaming (WebSockets/Kafka) to trigger automatic re-routing.
- **Multi-Modal Transit Routing**: Expand route optimizer to incorporate metro lines and bus corridors.
- **Deep Sequence Model**: Train LSTM / Transformer time-series predictor using TensorFlow/PyTorch if multi-day seasonal traffic forecasting is required.
- **Distributed Caching**: Expand Redis cache clustering for high-throughput city-wide deployment.

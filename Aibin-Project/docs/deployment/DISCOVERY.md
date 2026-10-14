# TrafficVision AI — Milestone 4 Discovery Report
**Author:** Intern 1 (Team Lead / Backend & Integration)  
**Date:** Milestone 4, Day 0 Discovery Phase  
**Target:** Production Deployment, Containerization & Integration Audit  

---

## 1. Executive Summary

TrafficVision AI is an intelligent traffic prediction and congestion management platform consisting of multiple specialized services developed across Milestones 1–3. As we transition into Milestone 4, the functional API contracts are **FROZEN**. Milestone 4 focuses entirely on production-grade containerization, API Gateway hardening, environment variable contract alignment, deployment runbooks, live workflow validation, and performance optimization.

This discovery audit inspects the `aibin-backend` repository as well as read-only partner workspaces (`anmol-data`, `saksham-aiml`, `hariom-frontend`) to identify the complete service landscape, port mappings, communication flows, environment configurations, and integration gaps.

---

## 2. Microservice & Architecture Inventory

| Service | Owner / Workspace | Tech Stack | Port | Entry Point | Health Endpoint | Upstream / Downstream Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **API Gateway & Auth** | Intern 1 (`aibin-backend`) | Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, JWT, Passlib/Bcrypt | `8080` | `app/main.py` | Need to add `/health` & `/ready` | Upstream: Auth DB. Downstream: All microservices |
| **Route Analysis** | Intern 1 (`aibin-backend`) | Python 3.11+, FastAPI, OSRM / OpenStreetMap HTTP client | `8002` | `route_analysis/main.py` | `/health` (liveness) & `/` (metadata) | Downstream: OSRM router (`router.project-osrm.org`), AI Engine (`:8001`) |
| **Alert Service** | Intern 1 (`aibin-backend`) | Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL | `8003` | `alert_service/main.py` | `/health` | Upstream: PostgreSQL (`alerts` table) |
| **Traffic Monitoring** | Intern 2 (`anmol-data`) | Python, FastAPI, psycopg3, Redis | `8000` | `Api/traffic_api.py` | `/` (returns status ok) | Upstream: PostgreSQL (`traffic_readings`, `sensors`, etc.), Redis (`traffic:live` cache) |
| **Traffic Analytics** | Intern 2 (`anmol-data`) | Python, FastAPI, psycopg3 | `8000` | `Api/traffic_api.py` | `/` (same app as Monitoring) | Upstream: PostgreSQL (`congestion_history`, `road_conditions`) |
| **AI / ML Prediction Engine**| Intern 3 (`saksham-aiml`)| Python, FastAPI, Scikit-learn, Joblib | `8001` | `ai_engine/main.py` | No `/health` (serves `/predict/*`, `/ai/*`) | Downstream: Joblib model artifact (`traffic_model_v2.joblib`), Alert Service (`:8003`) |
| **Frontend Application** | Intern 4 (`hariom-frontend`)| Next.js 15, React 19, TypeScript, Tailwind CSS v4, Leaflet | `3000` (dev) | Next.js App Router | Next.js built-in | Calls API Gateway (`:8080/api/v1`) |

---

## 3. Communication Topology & Flow

All external client traffic (Web UI, Mobile, External API consumers) flows **strictly through the API Gateway** on Port `8080`. The microservices reside in an isolated backend network.

```
+-----------------------------------------------------------------------------------+
|                                Client Layer                                       |
|  Hariom Frontend (Next.js :3000)   /   External API Clients / Admins / Commuters  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v (HTTP / HTTPS / JWT)
+-----------------------------------------------------------------------------------+
|                        API Gateway & Auth Service (:8080)                         |
|   - Authentication & JWT Token Issuance (/api/v1/auth)                            |
|   - Role-Based Access Control (RBAC: Admin, Operator, Planner, Commuter)           |
|   - Security Headers, Strict CORS, Global & Endpoint Rate Limiting                |
+-----------------------------------------------------------------------------------+
         |                    |                   |                   |
         v                    v                   v                   v
+------------------+ +------------------+ +------------------+ +--------------------+
| Traffic &        | | AI Prediction    | | Route Analysis   | | Alert Service      |
| Analytics Service| | Engine           | | Service          | |                    |
| (anmol-data)     | | (saksham-aiml)   | | (aibin-backend)  | | (aibin-backend)    |
| Port: 8000       | | Port: 8001       | | Port: 8002       | | Port: 8003         |
+------------------+ +------------------+ +------------------+ +--------------------+
         |                    |                                          |
         +--------------------+------------------------------------------+
                              |
                     +------------------+
                     | Storage & Cache  |
                     | PostgreSQL: 5432 |
                     | Redis: 6379      |
                     +------------------+
```

---

## 4. Current State & Configuration Audit

### 4.1 Existing Docker & Compose Config
- `aibin-backend/Dockerfile`: Simple single-stage Dockerfile based on `python:3.11-slim`, installs all `requirements.txt`, runs `uvicorn app.main:app` on port 8000 as root. Needs multi-stage build, non-root user, proper healthcheck, and production flags.
- `aibin-backend/alert_service/Dockerfile`: Minimal Dockerfile based on `python:3.10-slim`, directly runs `pip install` without requirements file, runs on port 8003 as root.
- `aibin-backend/docker-compose.yml`: Development compose file wiring `gateway` (8080), `route-analysis` (8002), `alert-service` (8003), and local `postgres` (5432). Uses obsolete `version: '3.8'` syntax and hardcoded dev credentials. Lacks Redis, production healthcheck dependencies, and resource limits.
- `.dockerignore`: Missing in `aibin-backend` root and subservices! Node artifacts, git folders, and caches could accidentally be copied into Docker contexts.

### 4.2 CI/CD Configuration
- `.github/workflows`: Currently absent in `aibin-backend`. Intern 5 will require a robust GitHub Actions workflow for linting, testing, Docker image building, and deployment verification.

### 4.3 Gateway Current Configuration
- **CORS**: Currently configured with wildcard `allow_origins=["*"]`. This is unsafe for production and fails standard security audits. Must be changed to read `CORS_ALLOWED_ORIGINS` dynamically with strict origins (e.g. frontend domain).
- **Rate Limiting**: Completely absent. Vulnerable to DoS and brute-force attacks on `/api/v1/auth/login`.
- **Security Headers & Reverse Proxy**: No `X-Forwarded-*` trusted proxy headers, no security headers (HSTS, X-Frame-Options, X-Content-Type-Options), no request IDs, and no structured logging.
- **Service URLs**: Hardcoded default URLs in `app/gateway/alert_proxy.py` (`http://127.0.0.1:8003`), while others use `app/config.py`. All upstream URLs must strictly load from environment variables.

---

## 5. Partner Workspaces Audit (Read-Only)

### 5.1 Intern 2 (`anmol-data`)
- **Database & Tables**: Managed via `Database/schema.sql` (defines `roads`, `sensors`, `road_capacity`, `traffic_readings`, `congestion_history`, `traffic_staging`, `road_conditions`).
- **Connection Configuration**: Reads `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` individually rather than parsing standard `DATABASE_URL`. Reads `REDIS_HOST`, `REDIS_PORT` rather than `REDIS_URL`.
- **Health Check**: Root `@app.get("/")` returns `{"message": "Traffic Monitoring Service is running", "status": "ok"}`. Does not expose `/health`.

### 5.2 Intern 3 (`saksham-aiml`)
- **Model Artifact**: `ai_engine/traffic_model_v2.joblib` loaded at startup.
- **Endpoints**: `/predict/congestion`, `/predict/delay`, `/predict/peak-hours`, `/predict/routes/rank`, `/ai/anomalies`, `/api/v1/ai/recommendations`.
- **Integration Vulnerability**: In `ai_engine/main.py` lines 307–318, `detect_traffic_anomaly` hardcodes `http://127.0.0.1:8003/api/v1/alerts`. In Docker and cloud containers, this fails because `127.0.0.1` targets the AI container itself, not the alert service. Recorded in `INTEGRATION_NOTES.md`.

### 5.3 Intern 4 (`hariom-frontend`)
- **Framework**: Next.js 15 (React 19, Tailwind CSS v4).
- **Gateway Contract**: `frontend/.env.local` expects `NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1`.
- **CORS Requirement**: The Gateway must allow `http://localhost:3000` for development and the production Vercel/Cloud frontend domain for production.

---

## 6. Comprehensive Environment Variable Inventory

| Variable Name | Used By | Required/Optional | Default / Example | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Gateway, Auth, Alert Service, Route Analysis | Required | `postgresql://user:pass@host:5432/dbname` | Primary PostgreSQL connection string |
| `REDIS_URL` | Gateway, Monitoring, Analytics | Required | `redis://redis:6379/0` | Redis caching & pub/sub connection string |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | `anmol-data` | Required (Intern 2) | `postgres`, `5432`, `postgres`, `postgres`, `password` | Split DB parameters required by `traffic_api.py` |
| `REDIS_HOST`, `REDIS_PORT` | `anmol-data` | Required (Intern 2) | `redis`, `6379` | Split Redis parameters required by `traffic_api.py` |
| `JWT_SECRET_KEY` | Gateway / Auth | Required (Secret) | `prod_secret_min_32_characters_random_hex` | Symmetric signing key for JWT tokens |
| `JWT_ALGORITHM` | Gateway / Auth | Optional | `HS256` | JWT cryptographic algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Gateway / Auth | Optional | `60` | Lifespan of access token in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Gateway / Auth | Optional | `7` | Lifespan of refresh token in days |
| `DATA_ENGINEERING_URL` / `TRAFFIC_SERVICE_URL` | Gateway, Route Analysis | Required | `http://traffic-monitoring:8000` | Internal URL for Intern 2 traffic service |
| `AI_ENGINE_URL` / `PREDICTION_SERVICE_URL` | Gateway, Route Analysis | Required | `http://ai-engine:8001` | Internal URL for Intern 3 AI engine |
| `ROUTE_ANALYSIS_URL` | Gateway | Required | `http://route-analysis:8002` | Internal URL for Route Analysis service |
| `ALERT_SERVICE_URL` | Gateway, AI Engine | Required | `http://alert-service:8003` | Internal URL for Alert Microservice |
| `OSRM_BASE_URL` | Route Analysis | Optional | `https://router.project-osrm.org` | OpenStreetMap routing engine API |
| `CORS_ALLOWED_ORIGINS` | Gateway | Required | `http://localhost:3000,https://trafficvision.vercel.app` | Comma-separated list of allowed origins |
| `RATE_LIMIT_GLOBAL_PER_MIN` | Gateway | Optional | `120` | Max requests per minute per IP |
| `RATE_LIMIT_AUTH_PER_MIN` | Gateway | Optional | `10` | Max auth/login attempts per minute per IP |
| `APP_ENV` | All Backend Services | Optional | `production` / `development` | Runtime environment flag |
| `PORT` | Gateway | Optional | `8080` | Bind port for Uvicorn |
| `LOG_LEVEL` | All Backend Services | Optional | `info` | Logging verbosity (`debug`, `info`, `warning`, `error`) |
| `TRUST_PROXIES` | Gateway | Optional | `true` | Forwarded headers trust flag for reverse proxies/ALB |

---

## 7. Next Actions for Milestone 4
1. **Day 1**: Formalize `M4_DEPLOYMENT_PLAN.md`, `ENV_VARS.md`, `.env.production.example`, and `INTEGRATION_NOTES.md`.
2. **Day 2**: Author production multi-stage Dockerfiles (`.dockerignore`, non-root user, healthchecks) and `docker-compose.prod.yml`.
3. **Day 3**: Implement production Gateway middlewares (strict CORS, rate limiting, request tracking, security headers, graceful shutdown) and `test-gateway.sh`.
4. **Day 4**: Write Cloud Deployment Runbook (`CLOUD_DEPLOY_RUNBOOK.md`), `smoke-test.sh`, and GitHub Actions CI workflow.
5. **Day 5**: Build live end-to-end validation suite (`validate-workflows.py` / `.sh`) and baseline validation report.
6. **Day 6**: Tune backend performance (caching, connection pooling, compression, latency benchmarking) and record defects in `DEFECT_LOG.md`.
7. **Day 7**: Finalize comprehensive documentation, demo runbook, and root `README.md`.

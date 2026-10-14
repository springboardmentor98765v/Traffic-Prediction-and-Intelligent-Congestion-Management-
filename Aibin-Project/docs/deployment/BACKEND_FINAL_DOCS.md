# TrafficVision AI — Final Backend & Deployment Documentation (Milestone 4)

**Role:** Intern 1 (Team Lead / Backend & Integration)  
**Project:** TrafficVision AI — Smart Traffic Prediction & Congestion Management System  
**Milestone:** 4 (Testing, Deployment & Documentation)  
**Status:** Live-Ready & Frozen Contract Compliant  

---

## 1. System Architecture Overview

TrafficVision AI is an intelligent microservices-based distributed platform that unifies real-time traffic monitoring, predictive machine learning, intelligent routing, automated alert notifications, and historical traffic analytics into an integrated smart-city dashboard.

The backend is coordinated through a hardened **API Gateway (Reverse Proxy & Auth Master)** which acts as the sole public gateway for client applications (Web Frontend, Mobile Apps, and Municipal Admin Consoles), routing requests internally to specialized domain microservices.

```
                      +-----------------------------+
                      |       Web Frontend /        |
                      |   Mobile Client (Port 3000) |
                      +--------------+--------------+
                                     |
                         HTTPS / RFC 6585 CORS
                                     v
                      +-----------------------------+
                      |         API GATEWAY         |
                      |   (Port 8080 / FastAPI)     |
                      |  - JWT Auth & RBAC Engine   |
                      |  - Sliding-Window Rate Limit|
                      |  - Request IDs & Logging    |
                      |  - GZip Compression         |
                      +--+-----+-----+-----+-----+--+
                         |     |     |     |     |
       +-----------------+     |     |     |     +-----------------+
       |                       |     |     |                       |
       v                       v     |     v                       v
+--------------+ +---------------+   |  +--------------+ +-------------------+
|  Traffic API | |  AI Engine    |   |  | Route Analysis| |   Alert Service  |
| (anmol-data) | |(saksham-aiml) |   |  |(aibin-backend)| |  (aibin-backend)  |
|  Port 8000   | |  Port 8001    |   |  |  Port 8002    | |    Port 8003      |
+------+-------+ +-------+-------+   |  +--------------+ +---------+---------+
       |                 |           |                             |
       +------------+----+           |                             |
                    |                v                             |
                    |     +--------------------+                   |
                    +---->|   Managed PostgreSQL| <-----------------+
                    |     | (Tables: users,    |
                    |     |  traffic, alerts)  |
                    |     +--------------------+
                    v
          +--------------------+
          |   Redis Cache      |
          | (Port 6379 / PubSub|
          +--------------------+
```

---

## 2. Microservice Registry & Port Allocation

| Service Name | Port | Owner | Tech Stack | Entry Point | Primary Responsibility |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **API Gateway** | `8080` | Intern 1 | Python 3.11 / FastAPI | `app.main:app` | Reverse proxy, JWT generation & verification, RBAC enforcement, rate limiting, request tracing. |
| **Traffic Monitoring** | `8000` | Intern 2 | Python 3.11 / FastAPI | `Api.traffic_api:app` | Real-time traffic density ingest, road telemetry, historical analytics and heatmaps. |
| **AI Engine / Prediction** | `8001` | Intern 3 | Python 3.11 / FastAPI | `ai_engine.main:app` | ML congestion forecasting, delay estimation, anomaly detection, AI recommendations. |
| **Route Analysis** | `8002` | Intern 1 | Python 3.11 / FastAPI | `route_analysis.main:app`| Multi-point route optimization, detour recommendations, incident-aware routing. |
| **Alert Service** | `8003` | Intern 1 | Python 3.11 / FastAPI | `alert_service.main:app` | Real-time congestion & accident alerts, acknowledgement tracking, pub/sub notifications. |
| **Frontend** | `3000` | Intern 4 | React / TypeScript | `src/index.tsx` | Responsive traffic dashboard, real-time map visualizer, operator incident dispatch. |
| **Redis Cache** | `6379` | Infra | Redis 7 Alpine | Container daemon | Live traffic caching, rate-limit state sync, inter-service broadcast. |
| **PostgreSQL Database**| `5432` | Intern 2 | PostgreSQL 16 | Managed Cloud DB | Persistent storage for users, historical traffic observations, and alerts. |

---

## 3. API Gateway Production Specifications

The API Gateway is hardened with enterprise-grade middleware:
1. **Strict CORS Policy:** Reads allowed origins from `CORS_ALLOWED_ORIGINS` (comma-delimited). Disallows wildcards (`*`) in production. Supports credentials for secure session cookie exchange.
2. **Dual-Tier Sliding-Window Rate Limiter:**
   - **Global Limit:** 600 requests/min per IP (prevents volumetric denial-of-service).
   - **Auth Limit:** 60 requests/min per IP on `/api/v1/auth/login` and `/api/v1/auth/register` (mitigates credential stuffing).
   - Returns RFC 6585 `HTTP 429 Too Many Requests` with `Retry-After` header.
3. **Security Headers (OWASP Recommended):**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains` (when running under HTTPS).
4. **Structured Access Logging & Distributed Tracing:**
   - Every request is tagged with an `X-Request-ID` UUID header (propagated downstream).
   - Standardized JSON/log format records client IP, HTTP method, route, duration in milliseconds, and status code.
5. **Response Compression:**
   - `GZipMiddleware` automatically compresses payloads > 1,000 bytes with ~70% bandwidth reduction.
6. **Unified Health Probes:**
   - `GET /health`: Instant liveness probe for load balancers.
   - `GET /ready`: Deep readiness probe verifying database connectivity.

---

## 4. Environment Variable Contract Summary

Full details in [ENV_VARS.md](file:///c:/Users/AIBIN%20SHIBU/OneDrive/Documents/trafficvision/aibin-backend/docs/deployment/ENV_VARS.md). Template in `.env.production.example`.

| Category | Key Variables | Description |
| :--- | :--- | :--- |
| **Database & Cache** | `DATABASE_URL`, `REDIS_URL` | PostgreSQL connection string and Redis URI. |
| **Security & Auth** | `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | HS256 secret key and token TTL. |
| **CORS & Networking**| `CORS_ALLOWED_ORIGINS`, `PORT`, `TRUST_PROXIES` | Domain allow-list (e.g. frontend URL) and port. |
| **Rate Limiting** | `RATE_LIMIT_GLOBAL_PER_MIN`, `RATE_LIMIT_AUTH_PER_MIN` | Sliding-window request thresholds. |
| **Upstream Services**| `TRAFFIC_SERVICE_URL`, `AI_ENGINE_URL`, `ROUTE_ANALYSIS_URL`, `ALERT_SERVICE_URL` | Internal service discovery hostnames. |

---

## 5. Docker & Containerization Architecture

All backend services run as multi-stage, rootless, pinned containers:
- **Base Image:** `python:3.11-slim` (minimal attack surface, ~150 MB).
- **User:** Non-root system user (`appuser`, UID 10001).
- **Production Compose File:** `docker-compose.prod.yml`
  - Deploys: `api-gateway`, `route-analysis`, `alert-service`, `traffic-service`, `ai-engine`, and `redis`.
  - Exposes **ONLY** port `8080` (Gateway) to the public host.
  - Inter-service communication takes place over the isolated bridge network `trafficvision_prod_net`.
  - Configured with `restart: unless-stopped`, healthcheck dependencies, and strict memory limits (300M–512M) suitable for 1 GB RAM cloud VMs.

### Common Docker Commands
```bash
# Validate production compose config
docker compose -f docker-compose.prod.yml config

# Build and start all services in background
docker compose -f docker-compose.prod.yml up --build -d

# Check running status & health
docker compose -f docker-compose.prod.yml ps

# View unified logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 6. Cloud Deployment Runbook

Follow the complete step-by-step instructions in [CLOUD_DEPLOY_RUNBOOK.md](file:///c:/Users/AIBIN%20SHIBU/OneDrive/Documents/trafficvision/aibin-backend/docs/deployment/CLOUD_DEPLOY_RUNBOOK.md).

Key Steps:
1. **[MANUAL]** Provision a free-tier Ubuntu 22.04 LTS instance (AWS EC2 t2.micro / Oracle Cloud / Render / Railway).
2. Configure 1 GB Swap space (`/swapfile`) to prevent OOM kills on Python ML imports.
3. Install Docker Engine and Docker Compose V2.
4. Clone the repository and provision `.env.production` from `.env.production.example`.
5. Launch stack via `docker compose -f docker-compose.prod.yml up -d`.
6. Run `scripts/smoke-test.sh http://<SERVER_IP>:8080`.
7. Configure Caddy or Nginx reverse proxy with Let's Encrypt SSL.

---

## 7. Security Best Practices

1. **Zero Secret Leakage:** No plaintext credentials committed to source code. All secrets injected through environment variables.
2. **Role-Based Access Control (RBAC):**
   - `admin`: Full access to all endpoints, operator dispatch, and active alert queries.
   - `traffic_operator`: Access to traffic density, incident alerts, and route condition updates.
   - `commuter`: Restricted to public route optimization, live traffic viewing, and congestion predictions.
3. **Payload Sanitization:** Max request body size capped at 10 MB (`MAX_REQUEST_BODY_SIZE_BYTES`) to prevent memory exhaustion attacks.
4. **Resilient Database Pooling:** Heartbeat probes (`pool_pre_ping=True`) prevent connection leaks on managed cloud PostgreSQL instances.

---

## 8. Troubleshooting Guide

| Issue / Symptom | Potential Root Cause | Diagnostic & Resolution Steps |
| :--- | :--- | :--- |
| **Gateway returns 502 Bad Gateway** | Downstream service is crashed or starting up. | Run `docker compose -f docker-compose.prod.yml ps` to check service health. Check upstream logs via `docker compose logs -f <service_name>`. |
| **Gateway returns 429 Too Many Requests** | Rate limit threshold exceeded. | Check `Retry-After` header. Adjust `RATE_LIMIT_GLOBAL_PER_MIN` or `RATE_LIMIT_AUTH_PER_MIN` in `.env.production`. |
| **Database Connection Refused / SSL Error** | Incorrect `DATABASE_URL` or sleeping cloud DB. | Verify `DATABASE_URL` in `.env.production`. Ensure PostgreSQL server allows SSL (`sslmode=require`). |
| **CORS Blocked in Browser** | Frontend URL not present in `CORS_ALLOWED_ORIGINS`. | Add frontend URL to `CORS_ALLOWED_ORIGINS` (e.g., `http://my-frontend.railway.app`) and restart Gateway. |
| **Container Killed (OOMKilled)** | Linux host ran out of physical memory. | Verify swap file is active: `free -m`. Check container memory limits in `docker-compose.prod.yml`. |

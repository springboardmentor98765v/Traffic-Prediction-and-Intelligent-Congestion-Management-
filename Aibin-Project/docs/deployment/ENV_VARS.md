# TrafficVision AI — Environment Variable Contract Specification
**Version:** 1.0.0 (Milestone 4 Production Contract)  
**Maintained by:** Intern 1 (Team Lead / Backend & Integration)  
**Scope:** Universal across all 5 Intern Services & Repositories  

---

## 1. Overview
This document specifies the authoritative, binding environment variable contract for TrafficVision AI Milestone 4. Every service reading environment configurations must adhere strictly to these variable names and semantics.

To ensure seamless operation between managed cloud providers and partner microservices, both unified connection URIs (e.g. `DATABASE_URL`, `REDIS_URL`) and legacy split parameters (e.g. `DB_HOST`, `DB_PORT`) are documented below.

---

## 2. Complete Environment Variable Contract Table

| Variable Name | Used by Which Services | Required / Optional | Example / Placeholder | Secret? (Yes/No) | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DATABASE_URL` | API Gateway, Auth, Alert Service, Route Analysis | **Required** | `postgresql://traffic_user:StrongPass123!@ep-xyz.neon.tech:5432/trafficvision_prod?sslmode=require` | **Yes** | Primary PostgreSQL connection string for SQL models (users, alerts, etc.). |
| `REDIS_URL` | API Gateway, Traffic Monitoring, Analytics | **Required** | `redis://redis:6379/0` (or `rediss://default:token@cloud-redis.upstash.io:6379`) | **Yes** | Connection URI for Redis cache and rate limiting. |
| `DB_HOST` | Intern 2 (`anmol-data`) | Required (for Intern 2) | `ep-xyz.neon.tech` or `postgres` | No | PostgreSQL host hostname/IP for discrete DB drivers. |
| `DB_PORT` | Intern 2 (`anmol-data`) | Optional | `5432` | No | PostgreSQL port number. |
| `DB_NAME` | Intern 2 (`anmol-data`) | Required (for Intern 2) | `trafficvision_prod` | No | PostgreSQL database name. |
| `DB_USER` | Intern 2 (`anmol-data`) | Required (for Intern 2) | `traffic_user` | No | PostgreSQL database username. |
| `DB_PASSWORD` | Intern 2 (`anmol-data`) | Required (for Intern 2) | `StrongPass123!` | **Yes** | PostgreSQL user password. |
| `REDIS_HOST` | Intern 2 (`anmol-data`) | Required (for Intern 2) | `redis` or `127.0.0.1` | No | Redis server hostname/IP for discrete Redis drivers. |
| `REDIS_PORT` | Intern 2 (`anmol-data`) | Optional | `6379` | No | Redis port number. |
| `JWT_SECRET_KEY` | API Gateway / Auth | **Required** | `c9f45d4e5f7a08b356417d91e843e91122a08f51a70cb47e923e3e01bc89a691` | **Yes** | High-entropy random 256-bit secret used to sign and verify HMAC-SHA256 JWT tokens. |
| `JWT_ALGORITHM` | API Gateway / Auth | Optional (Default: `HS256`) | `HS256` | No | Signing algorithm for JWT tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | API Gateway / Auth | Optional (Default: `60`) | `60` | No | Time-to-live (TTL) for short-lived access JWT tokens. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | API Gateway / Auth | Optional (Default: `7`) | `7` | No | Time-to-live for long-lived refresh tokens. |
| `DATA_ENGINEERING_URL` | API Gateway, Route Analysis | **Required** | `http://traffic-monitoring:8000` (prod) or `http://127.0.0.1:8000` (dev) | No | HTTP URL pointing to Intern 2's Traffic Monitoring & Analytics API. |
| `TRAFFIC_SERVICE_URL` | API Gateway | Optional (Alias) | `http://traffic-monitoring:8000` | No | Fallback alias for `DATA_ENGINEERING_URL`. |
| `AI_ENGINE_URL` | API Gateway, Route Analysis | **Required** | `http://ai-engine:8001` (prod) or `http://127.0.0.1:8001` (dev) | No | HTTP URL pointing to Intern 3's AI/ML Inference Engine. |
| `PREDICTION_SERVICE_URL`| API Gateway | Optional (Alias) | `http://ai-engine:8001` | No | Fallback alias for `AI_ENGINE_URL`. |
| `ROUTE_ANALYSIS_URL` | API Gateway | **Required** | `http://route-analysis:8002` (prod) or `http://127.0.0.1:8002` (dev) | No | HTTP URL pointing to Intern 1's Route Analysis Microservice. |
| `ALERT_SERVICE_URL` | API Gateway, AI Engine | **Required** | `http://alert-service:8003` (prod) or `http://127.0.0.1:8003` (dev) | No | HTTP URL pointing to Intern 1's Alert Microservice. |
| `OSRM_BASE_URL` | Route Analysis Microservice | Optional | `https://router.project-osrm.org` | No | Base URL for open-source OpenStreetMap / OSRM routing requests. |
| `MAPS_API_KEY` | Route Analysis, Frontend | Optional | `pk_test_osm_placeholder` | **Yes** | Key for third-party map tiling if Mapbox/Google Maps tiles are enabled (OSRM itself is keyless). |
| `CORS_ALLOWED_ORIGINS` | API Gateway | **Required** | `http://localhost:3000,https://trafficvision.vercel.app` | No | Comma-separated allow-list of origins permitted to make cross-origin requests. Wildcard `*` disabled in production. |
| `RATE_LIMIT_GLOBAL_PER_MIN` | API Gateway | Optional (Default: `120`) | `120` | No | Maximum allowed API requests per minute per client IP address before HTTP 429 is returned. |
| `RATE_LIMIT_AUTH_PER_MIN` | API Gateway | Optional (Default: `10`) | `10` | No | Stricter rate limit on `/api/v1/auth/login` to prevent credential brute-forcing. |
| `APP_ENV` / `NODE_ENV` | All Services | Optional (Default: `production`) | `production` | No | Runtime environment mode (`production`, `development`, `test`). |
| `PORT` | API Gateway, Microservices | Optional | `8080` (Gateway), `8000`, `8001`, `8002`, `8003` | No | TCP port on which each respective service listens. |
| `HOST` | All Services | Optional (Default: `0.0.0.0`) | `0.0.0.0` | No | Network interface bind address (`0.0.0.0` in Docker). |
| `LOG_LEVEL` | All Services | Optional (Default: `info`) | `info` | No | Minimum logging level (`debug`, `info`, `warning`, `error`). |
| `TRUST_PROXIES` | API Gateway | Optional (Default: `true`) | `true` | No | When `true`, trusts `X-Forwarded-For` and `X-Forwarded-Proto` headers from edge load balancers / reverse proxies. |
| `FORCE_HTTPS` | API Gateway | Optional (Default: `false`) | `false` | No | When `true`, automatically redirects insecure HTTP requests to HTTPS. |
| `NEXT_PUBLIC_API_URL` | Intern 4 (`hariom-frontend`) | **Required** (for Frontend) | `https://api.trafficvision.yourdomain.com/api/v1` | No | Public base API URL consumed by the client-side Next.js browser app. |

---

## 3. Environment Variable Grouping by Service

### Group 1: API Gateway & Auth (`:8080`)
```env
APP_ENV=production
PORT=8080
HOST=0.0.0.0
LOG_LEVEL=info
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=<generate_secure_random_hex_32_chars>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://trafficvision.vercel.app
RATE_LIMIT_GLOBAL_PER_MIN=120
RATE_LIMIT_AUTH_PER_MIN=10
TRUST_PROXIES=true
FORCE_HTTPS=false
DATA_ENGINEERING_URL=http://traffic-monitoring:8000
AI_ENGINE_URL=http://ai-engine:8001
ROUTE_ANALYSIS_URL=http://route-analysis:8002
ALERT_SERVICE_URL=http://alert-service:8003
```

### Group 2: Route Analysis Service (`:8002`)
```env
SERVICE_PORT=8002
OSRM_BASE_URL=https://router.project-osrm.org
AI_ENGINE_URL=http://ai-engine:8001
DATA_ENGINEERING_URL=http://traffic-monitoring:8000
MAPS_API_KEY=
```

### Group 3: Alert Microservice (`:8003`)
```env
PORT=8003
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Group 4: Traffic & Analytics Service (`:8000` - Intern 2)
```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=<db_password>
REDIS_HOST=redis
REDIS_PORT=6379
```

### Group 5: AI Inference Engine (`:8001` - Intern 3)
```env
PORT=8001
ALERT_SERVICE_URL=http://alert-service:8003
```

### Group 6: Frontend (`:3000` - Intern 4)
```env
NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
```

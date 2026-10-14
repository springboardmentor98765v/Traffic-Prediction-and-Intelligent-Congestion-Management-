# TrafficVision AI — Production API Gateway Specification
**Author:** Intern 1 (Team Lead / Backend & Integration)  
**Milestone:** Milestone 4  
**Component:** Edge API Gateway & Authentication Service (`:8080`)  
**Status:** Production Ready  

---

## 1. Overview
The API Gateway serves as the single public entry point for all TrafficVision AI traffic. In Milestone 4, the Gateway has been hardened for production deployment with enterprise-grade security policies, dynamic CORS negotiation, adaptive rate limiting, and structured observability.

---

## 2. Hardened Architecture & Features

### 2.1 Dynamic Strict CORS Policy
* **Environment Variable:** `CORS_ALLOWED_ORIGINS`
* **Behavior:**
  - Wildcard `"*"` is **strictly prohibited** in production mode (`APP_ENV=production`).
  - Supports comma-separated strings or JSON arrays (e.g. `http://localhost:3000,https://trafficvision.vercel.app`).
  - Permitted HTTP Methods: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`.
  - Credentials: `allow_credentials=True` (supports cookies and authorization headers).
  - Exposes headers: `X-Request-ID`, `Retry-After`.

### 2.2 Dual-Tier Rate Limiting
* **Implementation:** `InMemoryRateLimiter` (`app/core/rate_limiter.py`) with sliding 60-second window buckets per client IP address.
* **Tiers:**
  1. **Global Limit:** `RATE_LIMIT_GLOBAL_PER_MIN` (Default: `120 req/min`) applied across all general API endpoints.
  2. **Auth Limit:** `RATE_LIMIT_AUTH_PER_MIN` (Default: `10 req/min`) applied strictly to `/api/v1/auth/login` and `/api/v1/auth/register` to prevent credential stuffing and brute-force attacks.
* **Response on Threshold Breach:**
  - HTTP Status: `429 Too Many Requests`
  - Response Header: `Retry-After: <seconds_until_earliest_slot>`
  - Response Body:
    ```json
    {
      "detail": "Too many requests. Rate limit exceeded. Please retry after 42 seconds."
    }
    ```
* **Bypass:** System probes (`/health`, `/ready`) are explicitly exempted from rate limiting.

### 2.3 Security Headers & HTTPS Readiness
Every response emitted by the Gateway includes standard security headers:
* `X-Content-Type-Options: nosniff` (Prevents MIME-type sniffing).
* `X-Frame-Options: DENY` (Mitigates clickjacking attacks).
* `X-XSS-Protection: 1; mode=block` (Enables browser XSS filtering).
* `Referrer-Policy: strict-origin-when-cross-origin`.
* `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` (Enforces HTTPS in production).
* **HTTPS Enforcement:** Configurable via `FORCE_HTTPS=true`. When enabled behind edge load balancers, non-HTTPS requests receive an immediate `301 Moved Permanently` redirect.
* **Proxy Awareness:** `TRUST_PROXIES=true` inspects `X-Forwarded-For` and `X-Forwarded-Proto` for accurate client attribution.

### 2.4 Payload Limiting & Request Tracing
* **Payload Limit:** Rejects incoming bodies exceeding `MAX_REQUEST_BODY_SIZE_BYTES` (10 MB default) with `413 Payload Too Large`.
* **Request ID:** Injects `X-Request-ID` UUID into every request context and echoes it back in response headers.
* **Structured Access Logging:** Emits structured logs recording `request_id`, client IP, HTTP method, path, response status, and execution latency in milliseconds.

### 2.5 Health & Readiness Probes
* **`GET /health`**: Fast liveness probe for container orchestrators and ALB health checks:
  ```json
  {
    "status": "healthy",
    "service": "api-gateway",
    "version": "1.0.0",
    "timestamp": 1728800000.0
  }
  ```
* **`GET /ready`**: Readiness probe executing a lightweight `SELECT 1` query against the PostgreSQL database:
  ```json
  {
    "status": "ready",
    "service": "api-gateway",
    "database": "connected"
  }
  ```
  Returns `503 Service Unavailable` if database connectivity drops.

---

## 3. Downstream Upstream Routing Table

| Frontend Route Prefix | Destination Microservice | Internal Prod URL | Auth Required |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/*` | Auth Service (Internal to Gateway) | Internal DB | Public (`/register`, `/login`), Bearer Token (`/me`, `/refresh`) |
| `/api/v1/traffic/*` | Traffic Monitoring (`anmol-data`) | `http://traffic-monitoring:8000/traffic/*` | Admin, Traffic Operator |
| `/api/v1/predict/*` | AI Prediction Engine (`saksham-aiml`) | `http://ai-engine:8001/*` | Authenticated Users |
| `/api/v1/route/*` | Route Analysis Service (`aibin-backend`) | `http://route-analysis:8002/api/v1/route/*`| Authenticated Users |
| `/api/v1/alerts/*` | Alert Microservice (`aibin-backend`) | `http://alert-service:8003/api/v1/alerts/*` | Authenticated Users (RBAC) |
| `/api/v1/analytics/*` | Analytics Service (`anmol-data`) | `http://traffic-monitoring:8000/analytics/*` | Admin, Operator, City Planner |

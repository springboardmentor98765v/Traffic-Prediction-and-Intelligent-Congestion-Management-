# TrafficVision AI — Defect Log (Milestone 4, Day 6)

**Author:** Intern 1 (Team Lead / Backend & Integration)  
**Milestone:** 4 (Testing, Deployment & Documentation)  
**Status Tracking:** All backend defects resolved and validated in local integration suite.

---

## Defect Summary Table

| Defect ID | Severity | Component | Summary | Status |
| :--- | :---: | :--- | :--- | :---: |
| **TV-DEF-001** | CRITICAL | Alert Service (`alert_service/routers/alerts.py`) | Silent RBAC bypass due to `pass` statement in role check | **RESOLVED** |
| **TV-DEF-002** | HIGH | API Gateway (`app/gateway/alert_proxy.py`) | Missing reverse proxy handler for `POST /api/v1/alerts` | **RESOLVED** |
| **TV-DEF-003** | HIGH | API Gateway (`app/gateway/alert_proxy.py`) | Hardcoded `http://localhost:8003` prevented Docker/cloud networking | **RESOLVED** |
| **TV-DEF-004** | HIGH | Database Layer (`app/database.py`, `alert_service/database.py`) | Lack of connection pooling & pre-ping dropped idle cloud PostgreSQL connections | **RESOLVED** |
| **TV-DEF-005** | MEDIUM | Alert Service (`alert_service/database.py`) | `DATABASE_URL` variable undefined before SQLite dialect check | **RESOLVED** |
| **TV-DEF-006** | MEDIUM | Rate Limiter (`app/config.py`, `app/core/rate_limiter.py`) | Rate limit default (120 req/min) choked multi-service integration test suites | **RESOLVED** |
| **TV-DEF-007** | LOW | Test Automation (`scripts/perf_check.py`, `scripts/validate-workflows.py`) | Pydantic `EmailStr` rejected `.local` test domains | **RESOLVED** |

---

## Detailed Defect Records

### TV-DEF-001: Silent RBAC Bypass in Alert Service
- **Description:** Commuters were able to call `GET /api/v1/alerts/active` and view admin-restricted alert fields.
- **Root Cause:** In `alert_service/routers/alerts.py`, role verification was implemented as:
  ```python
  if x_user_role not in ["admin", "traffic_operator"]:
      pass  # Execution fell through!
  ```
- **Fix:** Replaced with explicit `HTTPException`:
  ```python
  if x_user_role not in ["admin", "traffic_operator"]:
      raise HTTPException(status_code=403, detail="Forbidden: insufficient permissions")
  ```
- **Verification:** Verified via `scripts/validate-workflows.py` Step 06; commuter token receives HTTP 403 Forbidden.

---

### TV-DEF-002: Missing `POST /api/v1/alerts` Reverse Proxy in Gateway
- **Description:** External clients and partner microservices forwarding alerts through the Gateway received HTTP 404 Not Found.
- **Root Cause:** Gateway reverse proxy only routed `GET /alerts/active` and `POST /alerts/{id}/read`; omitted the base creation route.
- **Fix:** Added `POST /api/v1/alerts` proxy handler in `app/gateway/alert_proxy.py` forwarding payload, headers, and `X-User-Role` upstream.
- **Verification:** Verified in `validate-workflows.py` Step 14 (`POST /api/v1/alerts` returns HTTP 201 Created).

---

### TV-DEF-003: Hardcoded Upstream URL in Gateway Alert Proxy
- **Description:** When running services in Docker Compose or isolated cloud containers, Gateway attempted to forward alerts to `http://localhost:8003` instead of the Docker service name.
- **Root Cause:** Hardcoded string `http://localhost:8003` inside `app/gateway/alert_proxy.py`.
- **Fix:** Refactored proxy to read `settings.ALERT_SERVICE_URL`.
- **Verification:** Tested in Docker compose configuration validation and dynamic env overrides.

---

### TV-DEF-004: Lack of Connection Pooling & Pre-Ping on PostgreSQL
- **Description:** Remote PostgreSQL databases (e.g., Supabase / RDS / Neon) terminate idle connections after 5–15 minutes, causing random `OperationalError: SSL connection has been closed unexpectedly`.
- **Root Cause:** SQLAlchemy engines initialized without explicit pool configuration or connection heartbeats.
- **Fix:** Added connection pooling in `app/database.py` and `alert_service/database.py`:
  ```python
  engine_kwargs["pool_size"] = 10
  engine_kwargs["max_overflow"] = 20
  engine_kwargs["pool_timeout"] = 30
  engine_kwargs["pool_recycle"] = 1800
  engine_kwargs["pool_pre_ping"] = True
  ```
- **Verification:** Verified persistent stability across consecutive 25-round benchmarks without socket errors.

---

### TV-DEF-005: Undefined `DATABASE_URL` in Alert Service
- **Description:** Alert service failed to initialize on startup with `NameError: name 'DATABASE_URL' is not defined`.
- **Root Cause:** Edit in `alert_service/database.py` inadvertently omitted assignment prior to `if DATABASE_URL.startswith("sqlite"):`.
- **Fix:** Restored `DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")`.
- **Verification:** Alert service starts cleanly and reports ready status.

---

### TV-DEF-006: Global Rate Limit Default Restricting Automated Validation
- **Description:** End-to-end load benchmarking scripts executing > 120 requests encountered HTTP 429 Too Many Requests.
- **Root Cause:** In `app/config.py`, `RATE_LIMIT_GLOBAL_PER_MIN` was defaulted to 120 instead of the planned production standard of 600.
- **Fix:** Raised default to 600 req/min in `app/config.py`, aligning with `.env.production.example`.
- **Verification:** Benchmark suite completed 150 consecutive requests with 100% success rate.

---

### TV-DEF-007: Pydantic `EmailStr` Validation Error on Test Domains
- **Description:** Registration of synthetic test users with domain `@trafficvision.local` failed with `HTTP 422 Unprocessable Entity`.
- **Root Cause:** Pydantic 2.x `EmailStr` adheres to RFC 6761 where `.local` is reserved for mDNS / local multicast.
- **Fix:** Standardized test automation in `perf_check.py` and `validate-workflows.py` to use `@trafficvision.ai`.
- **Verification:** User registration returns HTTP 201 Created reliably.

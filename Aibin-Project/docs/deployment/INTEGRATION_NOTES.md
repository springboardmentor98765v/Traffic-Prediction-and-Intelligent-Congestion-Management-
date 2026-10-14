# TrafficVision AI — Cross-Service Integration Notes
**Maintained by:** Intern 1 (Team Lead / Backend & Integration)  
**Status:** Active Tracking for Milestone 4 Cloud Deployment  

---

## 1. Purpose of this Document
In accordance with Rule 2 of Milestone 4, code inside partner repositories (`anmol-data`, `saksham-aiml`, `hariom-frontend`) is **READ-ONLY** for Intern 1. When an environment mismatch, configuration inconsistency, or operational risk is detected in a partner codebase, it is recorded here as a clear, actionable message to the owning intern detailing what was found, the exact file location, and the suggested resolution.

---

## 2. Open Issues for Partner Interns

### Issue TV-INT-001: Hardcoded Localhost Alert Service URL in AI Engine
* **Target Intern:** Intern 3 (`saksham-aiml`)
* **File Location:** `saksham-aiml/ai_engine/main.py`, lines 307–318
* **Problem:** In the anomaly detection handler (`detect_traffic_anomaly`), the alert callback makes an HTTP POST request to:
  ```python
  requests.post("http://127.0.0.1:8003/api/v1/alerts", json={...}, timeout=5)
  ```
  In Docker Compose and multi-container cloud deployments (such as Render, Railway, or an EC2 VM), each service runs in its own network namespace. Calling `http://127.0.0.1:8003` attempts to connect to the AI engine container itself rather than the Alert Service container, causing `requests.exceptions.ConnectionError` and dropping anomaly alerts.
* **Suggested Fix:**
  Read the Alert Service URL from an environment variable with fallback:
  ```python
  import os
  ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert-service:8003")
  ...
  requests.post(f"{ALERT_SERVICE_URL}/api/v1/alerts", json={...}, timeout=5)
  ```

---

### Issue TV-INT-002: Missing Standard `/health` Endpoint in AI Engine
* **Target Intern:** Intern 3 (`saksham-aiml`)
* **File Location:** `saksham-aiml/ai_engine/main.py`
* **Problem:** The AI Engine has no root `/health` or `/` endpoint. Container orchestrators (Docker Compose `healthcheck`, AWS ECS/App Runner, Render, Railway) require a fast, lightweight liveness probe to verify that the container is ready to accept traffic before directing queries to it. Currently, health probes targeting `/` receive `404 Not Found`.
* **Suggested Fix:**
  Add a lightweight health check endpoint:
  ```python
  @app.get("/health", tags=["Health"])
  def health_check():
      return {
          "status": "healthy",
          "service": "ai-engine",
          "model_loaded": model_artifact is not None
      }
  ```

---

### Issue TV-INT-003: Database & Cache Connection Variable Divergence
* **Target Intern:** Intern 2 (`anmol-data`)
* **File Location:** `anmol-data/Api/traffic_api.py`, lines 235–246
* **Problem:** `traffic_api.py` connects to PostgreSQL and Redis using discrete variables:
  ```python
  "host": os.getenv("DB_HOST", "127.0.0.1"),
  "port": int(os.getenv("DB_PORT", "5432")),
  "dbname": os.getenv("DB_NAME", "postgres"),
  "user": os.getenv("DB_USER", "postgres"),
  "password": os.getenv("DB_PASSWORD", "A")
  ```
  and `REDIS_HOST`, `REDIS_PORT`. However, standard managed cloud databases (AWS RDS, Neon, Supabase, Render Postgres) provide a single connection URI string: `DATABASE_URL` / `REDIS_URL`.
* **Backend Mitigation (Intern 1):** In `docker-compose.prod.yml` and `ENV_VARS.md`, Intern 1 supplies **both** `DATABASE_URL`/`REDIS_URL` and the discrete `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `REDIS_HOST`, `REDIS_PORT` to ensure full backward compatibility.
* **Suggested Fix for Intern 2:**
  Support connection URI fallback when `DATABASE_URL` is provided:
  ```python
  db_url = os.getenv("DATABASE_URL")
  if db_url:
      conn = psycopg.connect(db_url)
  ```

---

### Issue TV-INT-004: Missing Standard `/health` Route in Traffic API
* **Target Intern:** Intern 2 (`anmol-data`)
* **File Location:** `anmol-data/Api/traffic_api.py`, lines 288–298
* **Problem:** The traffic API implements its health check at `GET /`, returning `{"message": "Traffic Monitoring Service is running", "status": "ok"}`. For consistency across the microservice mesh, standard `/health` endpoints are preferred by Kubernetes and Docker healthchecks.
* **Suggested Fix for Intern 2:**
  Add an alias route:
  ```python
  @app.get("/health", tags=["Health"])
  def health():
      return root()
  ```

---

### Issue TV-INT-005: Frontend Production Gateway URL Configuration
* **Target Intern:** Intern 4 (`hariom-frontend`)
* **File Location:** `hariom-frontend/frontend/.env.local`
* **Problem:** The local frontend configuration sets:
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8080/api/v1
  ```
  When deploying the Next.js frontend to production (e.g. Vercel or cloud VM), this must be replaced with the public HTTPS URL of the deployed API Gateway (e.g. `https://api.trafficvision.yourdomain.com/api/v1` or cloud VM public IP/domain).
* **Action for Intern 4:** In the production hosting platform (e.g., Vercel Project Settings > Environment Variables), configure `NEXT_PUBLIC_API_URL` with the production Gateway URL provided by Intern 1.

---

## 3. Resolved Integration Items
* **TV-INT-R001:** Alert Proxy routing in API Gateway updated to correctly proxy all alert operations (`/my`, `/{id}/read`, `/active`, `POST /`).
* **TV-INT-R002:** Added AI anomalies and recommendations proxy endpoints (`/api/v1/predict/anomalies`, `/api/v1/predict/recommendations`) to the Gateway to bridge Intern 3's M3 deliverables.

---

## 4. Known Integration Issues & Runtime Mitigations

### 4.1 Cross-Container Network Resolution in Production
* **Symptom:** In local bare-metal development, services communicate via `127.0.0.1:<PORT>`. In multi-container Docker Compose and cloud environments, each container has its own `127.0.0.1` loopback interface.
* **Mitigation:**
  - Intern 1's API Gateway proxies dynamically use service names: `http://traffic-monitoring:8000`, `http://ai-engine:8001`, `http://route-analysis:8002`, `http://alert-service:8003`.
  - For local development, defaults safely fall back to `127.0.0.1`.

### 4.2 Database Table Initialization Race Condition
* **Symptom:** In local development, the Gateway lifespan creates `User` and `RefreshToken` tables, while `alert_service` lifespan creates `Alert` tables, and `schema.sql` creates sensor tables. If multiple services start concurrently against an empty cloud database, race conditions or foreign key errors can occur.
* **Mitigation:**
  - Pre-run `database/schema.sql` during cloud DB provisioning before launching backend containers.
  - Gateway and Alert Service safely use `create_all(bind=engine)` which uses `CREATE TABLE IF NOT EXISTS` semantics.

### 4.3 Redis Resilience Fallback
* **Symptom:** If Redis restarts or is temporarily unavailable, traffic monitoring or rate limiting must not fail hard.
* **Mitigation:**
  - Traffic Monitoring implements graceful `try/except (redis.RedisError)` fallback to database queries.
  - Gateway rate limiter utilizes memory tracking with thread-safe lock and periodic cleanup.


# TrafficVision AI — Backend & API Gateway

TrafficVision AI is an intelligent smart-city platform for real-time traffic monitoring, machine learning congestion forecasting, route optimization, incident alerting, and urban mobility analytics.

This repository (`aibin-backend`) contains the **Central API Gateway**, the **Route Analysis Microservice**, the **Alert & Incident Management Microservice**, along with the production containerization, CI/CD, and integration tooling for the entire platform.

---

## 1. Quick-Start (Local Development)

### 1.1 Prerequisites
- Python 3.11+
- Virtual environment (`venv`)
- PostgreSQL 16 (or local SQLite for lightweight testing)
- Redis 7 (optional for local dev, recommended for caching)

### 1.2 Setup & Run
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # On Linux/macOS
# or .venv\Scripts\activate     # On Windows

# 2. Install dependencies
pip install -r requirements.txt
pip install -r alert_service/requirements.txt
pip install -r route_analysis/requirements.txt

# 3. Configure local environment
cp .env.example .env

# 4. Start the API Gateway
uvicorn app.main:app --port 8080 --reload
```

Interactive OpenAPI Swagger UI is available at:
👉 **http://localhost:8080/docs**

---

## 2. Production Deployment Summary (Milestone 4)

In Milestone 4, the platform was containerized and hardened for free-tier cloud environments (e.g., Ubuntu 22.04 LTS on AWS EC2 / Render / Railway):

- **Architecture:** Single public entry point via API Gateway (`port 8080`), routing internally across an isolated Docker bridge network.
- **Database:** Managed Cloud PostgreSQL (e.g., Supabase / Neon / RDS) via `DATABASE_URL` with pre-configured connection pooling and heartbeat pre-ping.
- **Security:** Strict CORS allow-list (`CORS_ALLOWED_ORIGINS`), dual-tier sliding window rate limiting (600 global / 60 auth per min), security headers (`nosniff`, `DENY`), and non-root rootless containers (`python:3.11-slim`).
- **Resilience:** GZip response compression (>1 KB), health/readiness probes (`/health`, `/ready`), and automated graceful shutdown handling.

### 2.1 Production Docker Compose Launch
```bash
# 1. Provision production environment configuration (no committed secrets)
cp .env.production.example .env.production
# Fill in real cloud secrets in .env.production

# 2. Validate configuration
docker compose -f docker-compose.prod.yml config

# 3. Build and launch all services in background
docker compose -f docker-compose.prod.yml up --build -d

# 4. Run automated smoke tests
./scripts/smoke-test.sh http://localhost:8080
```

---

## 3. Milestone 4 Documentation Index

All Milestone 4 engineering documentation is located under `docs/deployment/`:

| Document | Description |
| :--- | :--- |
| **[DISCOVERY.md](docs/deployment/DISCOVERY.md)** | Initial code discovery, ports, service boundaries, and contract analysis. |
| **[M4_DEPLOYMENT_PLAN.md](docs/deployment/M4_DEPLOYMENT_PLAN.md)** | Mermaid architecture diagram, cloud target comparison, team responsibilities, and startup order. |
| **[ENV_VARS.md](docs/deployment/ENV_VARS.md)** | Unified environment variable contract across all 5 teammates. |
| **[GATEWAY_PRODUCTION.md](docs/deployment/GATEWAY_PRODUCTION.md)** | API Gateway production hardening, CORS, rate limiting, and security header specs. |
| **[CLOUD_DEPLOY_RUNBOOK.md](docs/deployment/CLOUD_DEPLOY_RUNBOOK.md)** | Step-by-step VM setup, Docker deployment, SSL termination, and rollback runbook. |
| **[INTEGRATION_NOTES.md](docs/deployment/INTEGRATION_NOTES.md)** | Cross-repo partner alignment notes and runtime mitigations (Intern 2, 3, 4). |
| **[WORKFLOW_VALIDATION_REPORT.md](docs/deployment/WORKFLOW_VALIDATION_REPORT.md)** | End-to-end 22-step validation suite results across all integrated services. |
| **[PERFORMANCE_REPORT.md](docs/deployment/PERFORMANCE_REPORT.md)** | Real latency & throughput measurements (p50, p95, p99, RPS) and GZip benchmarks. |
| **[DEFECT_LOG.md](docs/deployment/DEFECT_LOG.md)** | Defect tracking table and resolution records for TV-DEF-001 through TV-DEF-007. |
| **[BACKEND_FINAL_DOCS.md](docs/deployment/BACKEND_FINAL_DOCS.md)** | Final comprehensive backend overview, architecture, security, and troubleshooting. |
| **[DEMO_SUPPORT.md](docs/deployment/DEMO_SUPPORT.md)** | Pre-flight checklist and talking points for live multi-service presentation. |

---

## 4. Automated Testing & Verification Tooling

- **`scripts/test-gateway.sh` / `scripts/test_gateway.py`**: Validates Gateway health, readiness, CORS allow/deny rules, and 429 rate limiter.
- **`scripts/smoke-test.sh` / `scripts/smoke_test.py`**: Rapid 7-check health probe verifying all services are up.
- **`scripts/validate-workflows.sh` / `scripts/validate-workflows.py`**: Complete 22-step end-to-end test verifying the full user journey (Auth -> Monitoring -> Prediction -> Route -> Alerts -> Analytics).
- **`scripts/perf-check.sh` / `scripts/perf_check.py`**: Latency and throughput benchmarking tool with GZip verification.

---

## 5. Change Control Policy

> **IMPORTANT:**  
> Once the TrafficVision AI platform is deployed live to production (Milestone 4, Day 3 onwards), **all production updates must go exclusively through the CI/CD pipeline** (`.github/workflows/backend-ci.yml`).  
> Direct manual edits, ad-hoc patching on production servers, or hot-patching running containers are strictly prohibited to ensure stability, reproducibility, and auditability.

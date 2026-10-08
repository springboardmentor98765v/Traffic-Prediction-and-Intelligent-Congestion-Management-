# TrafficVision AI — Milestone 3 QA Test Plan

## 1. Project

TrafficVision AI — Smart Traffic Prediction & Congestion Management System

## 2. Milestone

Milestone 3 — Alerts, Analytics & AI Insights

## 3. QA Owner

Intern 5 — QA, DevOps & Release Engineering

## 4. Testing Objective

Verify that the new Milestone 3 services (Alert Service, Analytics Service, AI Insights) work
correctly, and that Milestone 1 & 2 functionality remains stable throughout the milestone.

## 5. Testing Areas

### 5.1 Alert Service

Test:

- Trigger correctness for congestion and accident/anomaly alerts
- RBAC-scoped alert visibility
- Notification delivery timing and reliability
- Alert payload/response structure

### 5.2 Analytics Service

Test:

- Trend accuracy
- Heatmap accuracy
- Query performance on larger historical datasets
- Response structure

### 5.3 AI Insights

Test:

- Anomaly detection correctness
- Recommendation relevance/quality
- Required response fields
- Invalid input handling

### 5.4 Frontend

Test:

- Alerts page (`Front-end/Front-end/Alerts.html`) — currently static/mock, no live API wiring
  observed as of Day 1; to be re-checked once Intern 1's endpoints land
- Analytics/insights visualizations (once available)
- Loading and error states

### 5.5 Regression Testing

Re-test:

- Authentication
- RBAC
- Live Traffic Monitoring
- Traffic Prediction
- Route Analysis
- Existing Milestone 1 & 2 frontend pages

### 5.6 Integration Testing

Verify that:

Authentication → Live Traffic → Prediction → Route Analysis → Alerts → Analytics → AI Insights →
Frontend

works correctly together.

## 6. Testing Methods

- Functional testing
- API testing
- Negative testing
- Integration testing
- Regression testing
- Performance sanity testing
- RBAC testing
- Automated testing using pytest
- Manual API testing using Postman

## 7. Test Environment

- Python / FastAPI
- PostgreSQL/TimescaleDB (`timescale/timescaledb:2.17.2-pg16`)
- Redis
- Docker Compose (`docker-compose.dev.yml`)
- Postman
- pytest
- GitHub Actions
- Swagger/OpenAPI

## 8. Defect Management

Defects will be recorded with:

- Defect ID
- Feature
- Description
- Severity
- Priority
- Steps to reproduce
- Expected result
- Actual result
- Status

See `defect_tracker.md` in this folder (carries forward still-open Milestone 2 defects and records
the Day 1 baseline verification).

## 9. Exit Criteria

Milestone 3 QA will be considered complete when:

- Critical defects are resolved
- Major functional tests pass for Alerts, Analytics, and AI Insights
- Integration tests pass across the full M1+M2+M3 stack
- Milestone 1 & 2 regression tests pass
- RBAC checks pass on alerts
- Performance sanity checks are completed
- Code-quality checks are completed on new M3 code
- Final QA report and Deployment Readiness Checklist are prepared

## 10. Deployment

Production deployment is explicitly out of scope for Milestone 3. The Day 7 Deployment Readiness
Checklist is a planning document only, prepared for Milestone 4 use — no deployment action is
taken during Milestone 3.

## 11. Day 1 Baseline Verification (real, executed 2026-09-24)

As part of "review the Milestone 1 & 2 QA setup," the existing automated suite was run against the
current `Team-1` branch before any Milestone 3 code exists, to confirm the starting baseline:

```
$ python -m pytest -q
3 failed, 1 passed, 152 warnings in 12.71s

FAILED tests/test_day4_api.py::test_auth_register_login_me_refresh_and_rbac
FAILED tests/test_day4_api.py::test_traffic_endpoints
FAILED backend/tests/test_route_analysis.py::test_optimize_route
```

Findings, logged in `defect_tracker.md`:

- The 2 `tests/test_day4_api.py` failures are a **pre-existing stale test file** calling old,
  unprefixed routes (`/api/auth/...`, `/api/traffic/...`) instead of the current
  `/api/v1/auth/...` / `/api/v1/traffic/...` contract paths fixed under Milestone 2 (DEF-M2-002,
  DEF-M2-003). Not a regression — the live routes work; the test file was never updated after
  those fixes. Tracked as **DEF-M3-001**.
- The `backend/tests/test_route_analysis.py::test_optimize_route` failure is expected outside
  Docker: it needs a live Postgres reachable at host `postgres`, which only resolves inside the
  `trafficvision_net` Compose network. Passes when run against the real Docker stack (per M2
  Day 5/7 integration reports). Not a new defect — environmental, tracked as **DEF-M3-002** for
  visibility (should be skipped/marked when run outside Docker, not silently failing).
- `docker compose -f docker-compose.dev.yml config` validates cleanly (Docker 29.7.2 available
  locally), aside from a cosmetic `version` key warning — tracked as **DEF-M3-003** (Low).

This baseline is the reference point for the Day 6 regression pass.

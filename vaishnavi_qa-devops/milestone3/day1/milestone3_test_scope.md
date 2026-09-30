# TrafficVision AI — Milestone 3 QA Test Scope

## 1. Purpose

The purpose of Milestone 3 QA testing is to validate the new Alert Service, Analytics Service, and
AI Insights module, while ensuring that all Milestone 1 and Milestone 2 features continue to work
correctly.

## 2. Scope

The following Milestone 3 features will be tested:

### Alert Service

- Alert trigger correctness (congestion, accident/anomaly-triggered alerts)
- RBAC-scoped alert visibility (public / operator / admin see the correct alert set)
- Notification delivery timing and reliability
- Alert-to-frontend delivery (Alerts page)

### Analytics Service

- Trend accuracy (traffic trend over time)
- Heatmap accuracy (density/congestion heatmap data)
- Query performance on historical datasets

### AI Insights

- Anomaly detection correctness
- Recommendation quality/relevance
- Response structure and required fields

### Integration

- Auth → Live Traffic → Prediction → Route Analysis → Alerts → Analytics → AI Insights → Frontend
  works correctly together end-to-end

### Docker / Local Environment

- `docker-compose.dev.yml` extended with Alert Service and Analytics Service
- Full local stack (M1 + M2 + M3) starts and passes health checks together

## 3. Regression Scope

Milestone 1 and Milestone 2 features will be re-tested to ensure Milestone 3 changes do not
introduce regressions:

- Authentication (register/login/refresh/`/me`)
- RBAC (admin/operator/user access boundaries)
- Live Traffic Monitoring (`/traffic/live`, `/road/{id}`, `/density`)
- Traffic Prediction (`/predict/congestion`, `/predict/delay`, `/predict/peak-hours`)
- Route Analysis (`/route/optimize`, `/route/alternate`)
- Frontend pages carried over from M1/M2 (Login, dashboards, Route Analysis, Live Maps)

## 4. Non-Functional Checks

- API response time (including alert delivery latency, analytics query latency)
- API error handling / input validation
- Authorization/RBAC on all new endpoints
- Static code quality (ESLint, Flake8/Black) on new M3 code
- Local Docker Compose integration

## 5. Out of Scope

Production deployment is explicitly out of scope for Milestone 3. The only deployment-related
output this milestone is the Deployment Readiness Checklist (a planning document, Day 7,
explicitly for Milestone 4 use — no deployment action is performed).

All testing will be performed in the local development/integration environment.

## 6. Current Status as of Day 1 (baseline)

As of 2026-09-24, no Alert Service, Analytics Service, or AI Insights code exists yet in any team
branch (`main`, `Team-1..4`, or any individual intern branch). Sections above define the intended
scope per the Milestone 3 SRS; test execution against real endpoints begins once Intern 1 (Alerts)
and Intern 2 (Analytics/AI Insights) land their API contracts, per the Day 2 contract-freeze
checkpoint.

## 7. QA Objective

The final objective is to confirm that the Milestone 3 features work correctly, integrate with
Milestone 1 & 2, and are ready for final QA sign-off on Day 7.

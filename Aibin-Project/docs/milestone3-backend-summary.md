# Milestone 3 - Backend Summary & Handoff

**Author**: Intern 1 (Team Lead / Backend & Integration)
**Date**: 2026-09-24

## 1. What Was Built
1. **Alert Service**: Built as a standalone microservice on port 8003. It tracks alerts with `type`, `severity`, `road_id`, `message`, `read`, and `created_at`.
2. **Gateway Proxies**: Extended the API Gateway to route `/api/v1/alerts/*` to the Alert Service, and `/api/v1/analytics/*` to Anmol's Data Service.
3. **RBAC for Alerts**: The API Gateway decodes the JWT and passes user identity/role downstream via custom headers (`x-user-id`, `x-user-role`). The Alert Service filters `GET /my` based on these roles (e.g., commuters only see public-safety alerts like accidents and closures).
4. **Trigger Scripts**: Created poller scripts inside `scripts/` to mimic internal async tasks that constantly monitor Saksham's AI models and route delays, emitting internal `POST /api/v1/alerts` when anomalies or severe delays occur.

## 2. Stubbed vs. Real Dependencies
- **Real**: 
  - `POST /api/v1/alerts` and the database integration for the Alert service is real.
  - Gateway routing and RBAC headers are real.
- **Stubbed**: 
  - `GET /api/v1/analytics/trends` is a blind proxy. If `anmol-data` isn't returning 200, the Gateway falls back to a stubbed generic response.
  - The AI anomaly trigger (`scripts/anomaly_poller.py`) handles the shape specified by Intern 3. If that endpoint is not ready, it will just swallow the HTTP error and keep polling.
  - `scripts/closure_delay_trigger.py` triggers closure alerts by hitting `route_analysis` in a loop.

## 3. Known Limitations
- Short-interval polling is the default notification mechanism. WebSockets were considered as a Day 5 stretch goal but deprioritized in favor of robust short-polling to avoid infra complexities before Milestone 4.
- `alert_service` runs locally on the same database instance as the gateway to save resources, but logically it is separated and has its own `models.py`.

## 4. Handoff Notes for Milestone 4 (and for Intern 4)
- **Frontend (Intern 4)**: 
  - To show notifications, poll `GET /api/v1/alerts/my` every ~30 seconds.
  - Once a user clicks an alert, hit `POST /api/v1/alerts/{alert_id}/read`.
  - For the analytics graphs, use `GET /api/v1/analytics/trends?road_id=x&range=day|week`.
- **QA (Intern 5)**: 
  - Test scripts (`simulate_congestion_trigger.py`, `anomaly_poller.py`, `closure_delay_trigger.py`) are located in `scripts/`. You can run them manually to trigger alerts for frontend testing.
  - Run `docker-compose -f docker-compose.yml up` to test the full stack containerized.

# Milestone 1 Test Scope

## In scope

| Area                     | Endpoints / components                                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Authentication (7.1)     | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `GET /api/v1/auth/me`                |
| RBAC                     | Role claim in the JWT, role-gated routes (403 for the wrong role), forged / expired / wrong-type tokens                    |
| Traffic Monitoring (7.2) | `GET /api/v1/traffic/live`, `GET /api/v1/traffic/road/{road_id}`, `GET /api/v1/traffic/density`, threshold congestion rule |
| Prediction stub (7.3)    | `GET /api/v1/predict/congestion?road_id=` on the AI Engine (`generated_by: "heuristic-v0"`) and through the gateway        |
| Gateway                  | `/health`, Swagger `/docs`, OpenAPI lists every frozen route                                                               |
| Frontend                 | `Login.html` → role dashboard redirect, page role guards, API client base URL, live KPI values                             |
| Local environment (7.4)  | `docker-compose.dev.yml` services and health, container env matches the compose file                                       |
| CI                       | `.github/workflows/ci.yml`: lint, build (import check) and test on PR; no deploy stage                                     |

## Out of scope for Milestone 1

- Route analysis (`/api/v1/route/*`) is Milestone 2.
- Alerts and Analytics services are Milestone 3. The alert routes are used here only because they are the gateway's role-gated routes for RBAC checks.
- The trained ML model's accuracy is Milestone 2.
- Production packaging, cloud hosting and deployment come after Milestone 4.
- Performance or load testing beyond "live data loads" (SRS has no Milestone 1 performance target).

## Roles under test

| Role             | JWT `role` claim | `/auth/me` role | Landing page              |
| ---------------- | ---------------- | --------------- | ------------------------- |
| Public/Commuter  | `user`           | `PUBLIC`        | `public dashboard.html`   |
| Traffic Operator | `operator`       | `OPERATOR`      | `operator dashboard.html` |
| Admin            | `admin`          | `ADMIN`         | `admin dashboard.html`    |

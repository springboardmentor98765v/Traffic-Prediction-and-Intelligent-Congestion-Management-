# TrafficVision AI — API Reference (production)

Base URLs (Render; replace if your subdomains differ):

| Service   | Base URL                                  | Interactive docs  |
| --------- | ----------------------------------------- | ----------------- |
| Gateway   | `https://tv-team1-backend.onrender.com`   | `/docs`, `/redoc` |
| Analytics | `https://tv-team1-analytics.onrender.com` | `/docs`           |
| AI Engine | `https://tv-team1-ai.onrender.com`        | `/docs`           |

Auth: `Authorization: Bearer <access_token>` from `/api/v1/auth/login`.
🔒 = token required. 🔑 = alert service key (`X-Alert-Service-Key`) or operator/admin token.
Every endpoint below is exercised by `QA/milestone4/day4/full_system_test.py`.

## Gateway — `/api/v1`

### Auth & RBAC

| Method | Path             | Body / params             | Success                                                       | Errors                                                                                         |
| ------ | ---------------- | ------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| POST   | `/auth/register` | `{name, email, password}` | 201                                                           | 409 email exists, 400 username taken, 422 domain not allowed (gmail/yahoo/outlook/nitpy.ac.in) |
| POST   | `/auth/login`    | `{email, password}`       | 200 `{access_token, refresh_token, role, …}`                  | 401                                                                                            |
| POST   | `/auth/refresh`  | `{refresh_token}`         | 200                                                           | 401                                                                                            |
| GET    | `/auth/me` 🔒    | —                         | 200 `{user_id, username, role}` (`PUBLIC`/`OPERATOR`/`ADMIN`) | 401                                                                                            |

New accounts are always `user` (shown as `PUBLIC`); operator/admin are assigned in the DB.

### Traffic monitoring

| Method | Path                                | Params             | Returns                      |
| ------ | ----------------------------------- | ------------------ | ---------------------------- |
| GET    | `/traffic/live`                     | —                  | latest reading per road      |
| GET    | `/traffic/road/{road_id}`           | —                  | road detail + latest reading |
| GET    | `/traffic/density`                  | —                  | network density summary      |
| GET    | `/traffic/history`                  | `road_id`, `limit` | historical readings          |
| GET    | `/traffic/aggregate`                | `road_id`          | aggregate stats              |
| GET    | `/traffic/road-condition/{road_id}` | —                  | road condition records       |
| GET    | `/traffic/metrics/hourly`, `/daily` | `road_id`, `limit` | pre-aggregated metrics       |

### Prediction (model-v1, scikit-learn 1.9.0)

| Method | Path                  | Params / body                                                                                                     |
| ------ | --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| GET    | `/predict/congestion` | `road_id` — prediction from the latest live reading                                                               |
| POST   | `/predict/congestion` | `{road_id, vehicle_count, density, avg_speed_kmph, road_capacity, road_length_km, hour, day_of_week, is_weekend}` |
| GET    | `/predict/peak-hours` | `road_id`                                                                                                         |
| GET    | `/predict/delay`      | `road_id`                                                                                                         |

### Route analysis 🔒

`origin` and `destination` as `lat,lng` (e.g. `11.9416,79.8083`). Invalid coordinates → 400;
map provider down → 503.

| Method | Path                 | Returns                                |
| ------ | -------------------- | -------------------------------------- |
| GET    | `/route/optimize`    | best route with congestion-aware score |
| GET    | `/route/alternate`   | alternate routes ranked                |
| GET    | `/route/travel-time` | travel time estimate                   |
| GET    | `/route/conditions`  | conditions along the route             |

### Alerts

| Method | Path                      | Auth | Body / notes                                                                                           |
| ------ | ------------------------- | ---- | ------------------------------------------------------------------------------------------------------ |
| POST   | `/alerts/`                | 🔑   | `{type, severity: Low/Medium/High/Critical, road_id, message}` → 201; no key → 403; bad severity → 422 |
| GET    | `/alerts/my`              | 🔒   | alerts visible to the caller's role (public: no Critical / accident)                                   |
| PATCH  | `/alerts/{alert_id}/read` | 🔒   | 200; unknown id → 404                                                                                  |

`GET /health` (no prefix) → `{"status": "ok"}`.

## Analytics

| Method | Path                                                                                                                                    | Params                                            | Notes                                        |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------- |
| GET    | `/`                                                                                                                                     | —                                                 | service info / health                        |
| GET    | `/api/v1/traffic/live`, `/road/{id}`, `/density`, `/history`, `/aggregate`, `/road-condition/{id}`, `/metrics/hourly`, `/metrics/daily` | as gateway                                        | Redis-cached live traffic                    |
| GET    | `/analytics/trends`                                                                                                                     | `road_id`, `start_date`, `end_date` (YYYY-MM-DD)  | unknown road 404, bad date 422, inverted 400 |
| GET    | `/analytics/heatmap`                                                                                                                    | `start_date`, `end_date`, `time_bucket=hour\|day` |                                              |
| GET    | `/analytics/reports`                                                                                                                    | `road_id`, `start_date`, `end_date`, `limit`      | CSV download (`text/csv`)                    |

## AI Engine

| Method | Path                         | Params / body                                                    |
| ------ | ---------------------------- | ---------------------------------------------------------------- |
| GET    | `/health`, `/`               | —                                                                |
| GET    | `/api/v1/ai/anomalies`       | optional `road_id` — normal / anomaly / possible incident        |
| GET    | `/api/v1/ai/recommendations` | `road_id` (unknown → 404)                                        |
| POST   | `/predict`                   | `{vehicle_count, density, avg_speed_kmph, road_id, time_of_day}` |
| GET    | `/predict/live`              | predictions for all live roads (calls the gateway)               |
| GET    | `/api/v1/predict/congestion` | `road_id` (calls the gateway)                                    |

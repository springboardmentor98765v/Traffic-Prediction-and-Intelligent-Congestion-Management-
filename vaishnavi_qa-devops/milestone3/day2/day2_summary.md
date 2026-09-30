# Milestone 3 — Day 2 Summary (Intern 5: QA, DevOps & Release Engineering)

Date: 2026-09-24

## Task (SRS Day 2)

Extend `docker-compose.dev.yml` to include the Alert Service and Analytics Service; verify the full
local stack (M1 + M2 + M3) still starts correctly.

## Checkpoints

- [x] **Local environment updated with new services.** Alert Service is live in the stack.
      The Analytics Service slot is added but can't start yet because Intern 2's code isn't in
      the repo (see Blockers).
- [x] **Confirmed the whole stack still starts correctly.** `down` then `up` brings all 3
      containers to `healthy` in about 23 s.
- [x] **No earlier features broken by the update.** 33/34 smoke checks pass. The one failure
      (`/route/alternate`) is a bug in the maps-API fallback path (DEF-M3-004), not a regression
      from the compose change.

## What changed in `docker-compose.dev.yml`

| Change                                                                                                                       | Why                                                                                                                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backend` build context and bind mount now point at `./backend (1)/backend/Intern_AI AND ML`, overridable with `BACKEND_DIR` | The old `./backend` path doesn't exist in this checkout, so the stack couldn't build at all. The new folder is the one where Intern 1's Alert Service (`/api/v1/alerts`) landed.                                                          |
| Alert Service served by the `backend` container                                                                              | Intern 1 built alerts as a router inside the same FastAPI gateway (`app/main.py` → `alerts.router`), not as a separate process, so no extra container is needed. The `alerts` table is created on startup.                                |
| New `analytics` service behind `profiles: ["analytics"]` (port 8001, context `ANALYTICS_DIR` or `./analytics-service`)       | Reserves the Analytics Service slot with DB/Redis wiring and `ALERT_API_URL=http://backend:8000/api/v1/alerts/`. Because it's profile-gated, a plain `up` skips it until Intern 2's code exists. Then `--profile analytics up` starts it. |
| `backend` healthcheck (`GET /health`)                                                                                        | Lets `analytics` use `depends_on: condition: service_healthy`, and makes "the stack started" something you can check.                                                                                                                     |
| `REDIS_HOST=redis`, `REDIS_PORT=6379` passed to backend                                                                      | `app/redis_cache.py` reads `REDIS_HOST` (default `localhost`), which would fail inside the container.                                                                                                                                     |
| `image: trafficvision-backend:dev`                                                                                           | Gives the image a fixed name so `up` reuses a local build (see DEF-M3-006).                                                                                                                                                               |
| Removed obsolete top-level `version:` key                                                                                    | Closes **DEF-M3-003**. `docker compose config` is now warning-free.                                                                                                                                                                       |

## Verification evidence

```
$ docker compose -f docker-compose.dev.yml config --services
postgres
redis
backend

$ docker compose -f docker-compose.dev.yml --profile analytics config -q   # exit 0

$ docker compose -f docker-compose.dev.yml down && docker compose -f docker-compose.dev.yml up -d
backend=healthy after 23s
backend   Up (healthy)
postgres  Up (healthy)
redis     Up (healthy)

$ docker exec trafficvision-postgres-dev psql -U traffic -d trafficvision -c '\d alerts'
 alert_id | type | severity | road_id | message | read | created_at   (+ ix_alerts_road_id)

$ python QA/milestone3/day2/stack_smoke_test.py
33/34 passed          (3 runs, identical; full table in stack_smoke_results.md)

$ docker exec trafficvision-backend-dev python -m pytest -q tests
1 failed, 1 passed    (test_optimize_route: 401, stale test sends no token — DEF-M3-002 updated)
```

Smoke coverage by area:

| Area                                                                                      | Checks | Pass   |
| ----------------------------------------------------------------------------------------- | ------ | ------ |
| System health                                                                             | 1      | 1      |
| M1 Auth + RBAC (register, login, `/me`, refresh, negative cases)                          | 6      | 6      |
| M2 Traffic Monitoring (live, road, density, history, aggregate, condition, hourly, daily) | 8      | 8      |
| M2 Prediction (congestion GET/POST, peak hours, delay)                                    | 4      | 4      |
| M2 Route Analysis (optimize, alternate, travel-time, conditions, no-token, bad coords)    | 6      | 5      |
| M3 Alerts (create ×2, validation, list user/admin, mark read, 404, role scoping ×2)       | 9      | 9      |
| **Total**                                                                                 | **34** | **33** |

## Day 2 (EOD) contract freeze: Alert Service snapshot

These Alert API contracts were observed live today (`/openapi.json`). This is the frozen baseline;
any change after today needs team sign-off.

| Method | Path                                           | Request                                                     | Success response                                                                                                                 |
| ------ | ---------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| POST   | `/api/v1/alerts/`                              | `{type, severity, road_id, message}` (all required strings) | `201 {alert_id, status: "created", road_id, message}`                                                                            |
| GET    | `/api/v1/alerts/my?role=user\|operator\|admin` | query `role` (default `user`)                               | `200 [ {alert_id, type, severity, road_id, message, read, created_at} ]`, newest first. `user` excludes `severity == "Critical"` |
| PATCH  | `/api/v1/alerts/{alert_id}/read`               | —                                                           | `200 {alert_id, read: true, message}` · `404` if unknown                                                                         |

Alert producers already written against this contract:
`m3_day2_congestion_watcher.py` (High/Severe congestion → `type: congestion`) and
`automate_accident_alerts.py` (anomaly `possible_incident` → `type: accident`, severity High).

Analytics and AI Insights contracts are **not frozen yet**. No Analytics endpoints exist.
`anomaly_detector.py` is available only as a library, with no HTTP endpoint.

### Update 2026-09-25: Analytics contract frozen (late, confirmed by Intern 2)

Intern 2 confirmed the Analytics contract is frozen for the current M3 build. Response shapes
below were observed live on :8001 the same day and are frozen with it. Any rename or removal
needs team sign-off.

| Method | Path                 | Params                                                    | Success response                                                                                                                                                                                                                                                                                                           |
| ------ | -------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GET    | `/analytics/trends`  | `road_id` (required), `start_date`, `end_date`            | `200 {road_id, source, daily_trends[], weekly_pattern[]}`. `daily_trends[]`: `road_id, time_period, avg/max_vehicle_count, avg_speed_kmph, avg/max_density, total_readings, high/severe_congestion_count, high/severe_congestion_percentage`. `weekly_pattern[]`: same plus `day_of_week, day_of_week_number, hour_of_day` |
| GET    | `/analytics/heatmap` | `start_date`, `end_date`, `time_bucket` = `hour` \| `day` | `200 {source, time_bucket, roads, time_buckets, grid[]}`. `grid[]`: `road_id, time_bucket, avg_vehicle_count, avg_speed_kmph, avg/max_density, congestion_score, congestion_level, total_readings, low/medium/high/severe_count`                                                                                           |
| GET    | `/analytics/reports` | `road_id`, `start_date`, `end_date`, `limit` (1–50000)    | `200 text/csv`, `Content-Disposition: attachment; filename="traffic_historical_report[_<road>].csv"`, `X-Report-Row-Count`. Columns: `road_id, sensor_id, reading_timestamp, vehicle_count, avg_speed_kmph, road_capacity, traffic_density_vehicles_per_km, congestion_level, latitude, longitude, source`                 |

Error behaviour Intern 2 has committed to fix (not frozen yet, retest pending): malformed
date → 400/422 (DEF-M3-009), unknown road → 404 and inverted range → 400/422 (DEF-M3-011),
IST report days (DEF-M3-010), CORS (DEF-M3-014).

AI Insights contract: still not frozen, no service (DEF-M3-017).

## New defects logged today (see `../day1/defect_tracker.md`)

- **DEF-M3-004 (Medium):** `/route/alternate` returns 500 when the OSRM maps API is unreachable.
- **DEF-M3-005 (High):** Alert RBAC is based on a client-supplied `?role=` query param with no
  JWT check, so anyone can read Critical alerts, create alerts, or mark alerts read.
- **DEF-M3-006 (Low, environment):** `docker compose build` fails on this machine because AVG
  Antivirus HTTPS scanning breaks pip's TLS inside the container.
- **DEF-M3-003:** closed. **DEF-M3-002:** updated (inside Docker it fails with 401, not a DB error).
- **DEF-M2-008:** re-confirmed. The container has scikit-learn 1.7.2 and the model was pickled
  with 1.9.0.

## Blockers / notes for the team

- **Analytics Service (Intern 2): no code in the repo yet.** The compose slot is ready. Intern 2
  needs to deliver a folder with a `Dockerfile` whose app listens on 8001 (`app.main:app`), or
  tell QA the real module path/port.
- **Root CI (`.github/workflows/ci.yml`)** still installs from `backend/requirements.txt`, and
  that path doesn't exist in this checkout. It needs to point at the real backend folder before
  the Day 6 quality gate means anything.
- The backend folder name (`backend (1)/backend/Intern_AI AND ML`) has spaces and parentheses.
  Compose handles it, but renaming it to `backend/` would simplify CI, scripts and docs. That
  needs team agreement.

# TrafficVision AI — Milestone 2 Defect Tracker

| Defect ID  | Feature | Description           | Severity | Priority | Status      | Assigned To |
| ---------- | ------- | --------------------- | -------- | -------- | ----------- | ----------- |
| DEF-M2-001 | Backend service (repo structure) | Real `app/` source has now landed and was delivered nested at `Backend/Backend/app/...` with its own embedded `.git`. QA flattened it to `backend/app/...` (matching `docker-compose.yml` and the test suite) and removed the nested `.git`. Added `conftest.py` at repo root so `backend/app/main.py`'s internal `from app...` imports (written assuming `backend/` itself is the import root, matching the Docker `WORKDIR /app` setup) resolve correctly under pytest. Backend intern should redeliver directly under `backend/` (lowercase, one level, no embedded `.git`) next time. | High | Medium | Fixed | QA (Intern 5) |
| DEF-M2-002 | Auth API routing | Was: `app.include_router(auth.router, tags=["Authentication"])` had no prefix. **Fixed** in the 2026-09-13 redelivery — `main.py` now includes `prefix="/api/v1/auth"`. Re-verified live end-to-end: register → 201, login → 200 with valid tokens, `/me` → 200. | Critical | High | **Fixed** (verified 2026-09-13) | Backend intern |
| DEF-M2-003 | Traffic Monitoring API routing | Was: double `/traffic` prefix. **Fixed** — `routes/traffic.py`'s own prefix removed, only `main.py`'s `/api/v1/traffic` remains. Re-verified live: `/live`, `/road/{id}`, `/density` all return 200 at the correct contract paths. | High | High | **Fixed** (verified 2026-09-13) | Backend intern |
| DEF-M2-004 | Route Analysis API routing | Was: double `/api/v1/route` prefix. **Fixed** — `route_analysis.py`'s own prefix removed. Re-verified live, authenticated: `/optimize` and `/alternate` both return 200 with real OSM-resolved route data at the correct contract paths. | High | High | **Fixed** (verified 2026-09-13) | Backend intern |
| DEF-M2-005 | Prediction API contract mismatch | **Resolved 2026-09-16** — Intern 1's redelivered `predict.py` adds `GET /api/v1/predict/congestion?road_id={id}&time={ts}`, matching the documented contract exactly (kept the old POST as a separate legacy route for backward compatibility, doesn't conflict). Re-verified live: `GET /predict/congestion?road_id=R001&time=2026-09-16T18:00:00` → `200 {"road_id":"R001","predicted_level":"Low","confidence":0.8967,"model_version":"model-v1"}` — exact contract shape. | Medium | Medium | **Fixed, verified live 2026-09-16** | AI/ML intern |
| DEF-M2-006 | Dead/broken module `app/security/auth.py` | `backend/app/security/auth.py` line 5 does `from security.config import SECRET_KEY, ALGORITHM` — missing the `app.` prefix, so this module would fail to import if anything ever used it. Currently unused (nothing imports it — `routes/auth.py` correctly uses `app.security.config` instead), so it doesn't block startup, but it should be fixed or removed to avoid confusion/future breakage. | Low | Low | Open | Backend intern |
| DEF-M2-007 | Route Analysis page — stale route data on control change | **Fixed, confirmed 2026-09-14 and reconfirmed 2026-09-15** — `runRouteAnalysis()` now properly resets and re-renders KPIs, corridor list, segment table, and map polyline on every destination/mode change. Re-verified live twice: first against mock fallback data (ETA changed 10min/8.4km → 9min/7.8km on destination change), then again against real backend data post-DEF-M2-019 fix (11.31min/8.5km → 10.6min/9km) — recalculation holds up under both mock and live data. | High | Medium | **Fixed** (verified live 2026-09-14/15) | Frontend intern |
| DEF-M2-008 | Unpinned `scikit-learn` version | `backend/requirements.txt` lists `scikit-learn` with no version pin. `backend/ai-engine/models/model-v1.joblib` was pickled with scikit-learn 1.9.0; the environment resolves 1.9.1, producing `InconsistentVersionWarning` on every load. Reproducibility/deployment risk for the ML model — a future install could break the pickle format entirely. Recommend pinning `scikit-learn==1.9.0` (or re-exporting the model under the current version). | Low | Medium | Open | Backend/ML intern |
| DEF-M2-009 | CI never ran backend's own tests | `pyproject.toml` had `testpaths = ["tests"]`, so `backend/tests/test_main.py` and `backend/tests/test_route_analysis.py` (written by the backend intern) never ran in CI or local `pytest`. Running them directly found `test_optimize_route` fails — independent confirmation of DEF-M2-004. QA fixed by changing `testpaths` to `["tests", "backend/tests"]`. | Medium | Medium | **Fixed** | QA (Intern 5) |
| DEF-M2-010 | CI "Verify backend import" step was silently broken | `.github/workflows/ci.yml`'s `python -c "import backend.app.main; ..."` step failed with `ModuleNotFoundError: No module named 'app'` (reproduced locally) because `backend/app/main.py`'s internal imports assume `backend/` itself is on `sys.path` (matching Docker's `WORKDIR /app`), which a bare `python -c` from repo root doesn't provide. QA fixed by adding `PYTHONPATH: backend` to both the "Run automated tests" and "Verify backend import" CI steps; re-verified locally. | Medium | Medium | **Fixed** | QA (Intern 5) |
| DEF-M2-011 | Backend flake8 violations concentrated in dead code | 164 of 275 backend flake8 violations sit in `backend/traffic_authentication_complete/app/main.py`, an unused, non-authoritative duplicate auth service (confirmed unused earlier — `app/main.py` is authoritative). Recommend deleting `traffic_authentication_complete/`, `app/src/`, and `app/security/auth.py` (also dead, DEF-M2-006) rather than reformatting unused code. | Low | Low | Open | Backend intern |
| DEF-M2-012 | ESLint false-positive `no-unused-vars` on `api.js` globals | `authAPI`, `predictAPI`, `routeAPI`, `getCongestionBadgeInfo`, `logout`, `getDashboardUrl` are flagged unused because `api.js` is a plain `<script>` (not a module) and these are consumed as implicit globals from inline `<script>` blocks in the HTML pages, which ESLint can't trace across files. Needs an ESLint config fix (e.g. `/* exported ... */` or a targeted override), not a code change. Two real issues in the same lint run: `no-useless-catch` in `authAPI.login`/`register` (dead try/catch, safe to remove). | Low | Low | Open | Frontend intern |
| DEF-M2-013 | Plaintext credential in `Data/M2_Day6_Traffic_Monitoring_/.env` | Same pattern as `backend/.env` (DEF-M2-008's sibling issue) — a real-looking DB password (`traffic123`) committed to a working `.env` file. No root `.gitignore` exists to prevent this from landing in git history on the next broad `git add`. Team-wide hygiene gap, not backend-specific. | Medium | Medium | Open | Data/Intern 2 + whole team (needs root `.gitignore`) |
| DEF-M2-015 | Frontend/backend port mismatch | Was: `api.js` pointed at `:8001`, backend runs on `:8000`. **Fixed** in the 2026-09-13 redelivery (`Front-end (3)/`) — `BASE_URL` now correctly says `:8000`. Re-verified: a plain `fetch()` from a `file://`-loaded page to `http://localhost:8000/health` succeeds (200), confirming no CORS block either. | High | High | **Fixed** (verified 2026-09-13) | Frontend intern |
| DEF-M2-016 | Signup role mismatch — only self-registration path is broken | **Fixed 2026-09-14** — `Login.html` now sends `role: 'user'` directly, and `authAPI.register()` also normalizes any incoming role variant (`public`→`user`, `traffic_operator`→`operator`) as defense-in-depth. Re-verified live via direct browser fetch: register now returns `201 { user_id, message }` (previously `422` enum rejection). | High | High | **Fixed** (verified live 2026-09-14) | Frontend intern |
| DEF-M2-017 | Login causes an infinite redirect loop for role="user" | **Fixed 2026-09-14** — `getRole()`, `setSession()`, and `getDashboardUrl()` now normalize `USER`→`PUBLIC`, and `guardPage()` has an anti-loop guard (redirects to `Login.html` instead of re-triggering itself if already on the target page). Re-verified live with a real `role: "user"` account through the actual login form (not a workaround): login redirects cleanly to `public dashboard.html`, page reaches `networkidle` (no loop), `sessionStorage.role` correctly reads `PUBLIC`. Confirmed no auto-redirect-on-load exists in `Login.html`, so the (theoretical) stale-session edge case if the anti-loop guard ever fires doesn't manifest in practice. | Critical | High | **Fixed** (verified live 2026-09-14) | Frontend intern |
| DEF-M2-018 | `apiFetch`'s multi-host retry logic aborts working requests, silently falls back to mock | **Fixed 2026-09-14** — `apiFetch()` simplified to a single direct call to `API_CONFIG.BASE_URL`, `TIMEOUT` raised to 10s. Re-verified live: real network requests to `/route/*` now complete successfully (200, confirmed via request-level network logging, not just app-level status). The visible symptom (app still shows mock data) persists for a *different* reason — see DEF-M2-019. | Critical | High | **Fixed** (root cause resolved; see DEF-M2-019 for the new issue surfaced underneath) | Frontend intern |
| DEF-M2-024 | `/traffic/live`, `/road/{id}`, `/density` were all hardcoded, shadowing the real DB-backed functions | **Found and fixed by QA 2026-09-16**, during the final RBAC/regression pass. `traffic.py`'s route handlers for these three endpoints were named `get_live_traffic()` and `get_road_traffic()` — the exact same names as the real, DB-backed functions imported from `traffic_service.py` at the top of the file. In Python, that rebinds the module-level name, permanently shadowing the import, so these endpoints always returned the hardcoded `SAMPLE_TRAFFIC_DATA` regardless of the database. Confirmed live before the fix: `/live` returned fixed timestamp `2026-08-26T22:00:00` for every road, every time. Fix: renamed the route handlers (`live_traffic_endpoint`, `road_traffic_endpoint`, `traffic_density_endpoint`) so they no longer shadow the imports, and had them actually call `get_live_traffic()`, `get_road_traffic()`, `get_density_summary()`. Re-verified live: `/live` now returns real seeded data (`vehicle_count: 34`, timestamp `2026-08-23T23:00:00` — genuinely from the CSV, not the hardcoded value). Full pytest suite re-run, same 3 pre-existing unrelated failures, no new regressions. Fixed file to hand to Backend intern: `backend/app/routes/traffic.py`. | High | High | **Fixed** (QA, verified live 2026-09-16) | QA (Intern 5), for Backend intern |
| DEF-M2-023 | **Database was never actually seeded — endpoints were serving fallback sample data, not real data** | Discovered while testing Intern 1's new `predict.py`: the live `trafficvision` database had only a `users` table — no `roads`, `traffic_readings`, or `road_conditions` tables existed at all. This means every "confirmed live with real data" result reported on Day 5 for `/traffic/history`, `/aggregate`, `/road-condition`, and `/live` was actually **`SAMPLE_FALLBACK_DATA`** (a hardcoded list in `traffic_service.py` that silently activates when the DB query fails) — real-looking, but not from the database. **Fixed by QA**: applied Intern 2's schema (`roads`, `traffic_readings`, `road_conditions` — from `backend/data/M2_Day7_Traffic_Monitoring_/database/schema.sql` + `sql/m2_day4_road_conditions.sql`) to the live Postgres, then loaded the real CSV data (`historical_traffic_4weeks_cleaned.csv`, `road_conditions.csv`) — 6 roads, 4032 traffic readings, 9 road conditions now genuinely in the database. Re-verified: `/traffic/history` now returns varied real values (density 6.8, 7.8 — not the flat fallback numbers). Note: the delivered `seed_db.py` would not have worked as-is even if run — its own `roads` insert only had `road_id`/`road_name`, missing the `road_capacity`/`road_length_km` columns the schema requires as `NOT NULL`. | High | High | **Fixed** (QA, 2026-09-16) | QA (Intern 5) |
| DEF-M2-021 | `predict.py`'s new GET endpoints crash — wrong shape assumed from `get_road_traffic()` | **Fixed 2026-09-16** — user directed QA to apply the fix directly rather than round-trip through Intern 1. `get_prediction_features()` in `predict.py` now reads `traffic["history"][0]["vehicle_count"]` etc. (the most recent reading), using the correct `updated_at` timestamp key. Re-verified live: `GET /predict/congestion?road_id=R001` → `200 {"predicted_level":"Low","confidence":0.9167,"model_version":"model-v1"}`; `GET /predict/delay?road_id=R001` → `200 {"estimated_delay_minutes":3.21,"confidence":0.6512}`. `peak-hours` re-confirmed unaffected. Full pytest suite re-run — same 3 pre-existing unrelated failures, no new regressions. Fixed file to hand to Intern 1: `backend/app/routes/predict.py`. | High | High | **Fixed** (QA, verified live 2026-09-16) | QA (Intern 5), for AI/ML intern |
| DEF-M2-022 | `get_road_condition()` queries the wrong table | **Fixed 2026-09-16** — same as above, fixed directly by QA. Query now joins `roads` (for the display name) to `road_conditions` (for the actual condition fields), ordered by `condition_timestamp DESC`, instead of selecting condition columns off `roads` itself. Re-verified live: `GET /traffic/road-condition/R001` → `200 {"road_name":"NH16","surface_condition":"hazard","status":"Active","incident_type":"waterlogging","description":"Waterlogging reported after heavy rainfall",...}` — genuine seeded data, not the generic fallback. Fixed file to hand to Intern 3: `backend/app/services/traffic_service.py`. | Medium | Medium | **Fixed** (QA, verified live 2026-09-16) | QA (Intern 5), for Backend intern |
| DEF-M2-020 | **Security: unauthenticated privilege escalation via self-registration** | **Fixed 2026-09-15** — `auth.py`'s register endpoint now hardcodes `role="user"` server-side regardless of what the client requests (comment in source: "SECURE FIX: Hardcode role to 'user' so public signups cannot choose admin/operator roles"). Re-verified live: registered with `role: "admin"` in the request body (still 201, request itself isn't rejected), then logged in and decoded the returned JWT — it genuinely contains `"role":"PUBLIC"`, not admin. The server-requested privilege escalation no longer works. | **Critical** | **Critical** | **Fixed** (verified live 2026-09-15) | Backend intern (Intern 3) |
| DEF-M2-019 | Route stub-detection check has swapped lat/lng, rejects all genuine backend responses | **Fixed 2026-09-15** — `ptToArr` now returns `[pt[1], pt[0]]`, correctly converting the backend's `[lng, lat]` GeoJSON points to `[lat, lng]` before the haversine comparison. **Re-verified live, full end-to-end, for the first time this milestone**: logged in for real, navigated to Route Analysis, and the data-source badge reads `● LIVE API` (not mock). ETA/distance show realistic decimal values (`11.31 mins`, `8.5 km`) instead of the old round mock numbers, and correctly update again on destination change (`10.6 mins`, `9 km`). This is the first confirmed real backend-to-frontend data flow of Milestone 2. | Critical | High | **Fixed** (verified live end-to-end 2026-09-15) | Frontend intern |
| DEF-M2-014 | `docker-compose.dev.yml` backend could never start | The `backend` service's `DATABASE_URL` fallback default was `postgresql+psycopg2://traffic:change_me@localhost:5432/trafficvision` — `localhost` inside a container refers to itself, not the `postgres` service, so the backend hung indefinitely on startup trying to reach a database that was never there. Also discovered `.env.dev` (required by `env_file:`) never existed in the repo, only `.env.dev.example` — meaning this file has likely never successfully started for anyone before. QA fixed both: created `.env.dev` from the example (per the README's own instructions) and corrected the fallback host to `postgres`. Verified end-to-end: `docker compose -f docker-compose.dev.yml up -d --build` now brings up all 3 containers healthy and `GET /health` returns `200 {"status":"ok"}`. | High | High | **Fixed** | QA (Intern 5) |

## Severity

* Critical — System/service unavailable or major functionality blocked
* High — Important functionality is not working
* Medium — Functionality partially affected
* Low — Minor issue/cosmetic problem

## Status

* Not Started
* Open
* In Progress
* Fixed
* Retest
* Closed

## Defect Reporting Format

### Defect ID

DEF-M2-XXX

### Feature

Feature/API name

### Description

Short description of the problem.

### Steps to Reproduce

1.
2.
3.

### Expected Result

What should happen.

### Actual Result

What actually happened.

### Severity

Critical / High / Medium / Low

### Priority

High / Medium / Low

### Status

Open / In Progress / Fixed / Retest / Closed

### Evidence

Screenshot/Postman response/log/test output.

# Day 6 — Regression Report (Milestone 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Per SRS Section 10.5 Day 6: "Regression-test all Milestone 1 features to confirm nothing broke."

**Overall verdict: FAIL.** Milestone 1's own features (Auth, Traffic Monitoring) are currently broken at the API level by Milestone 2 changes — this is exactly the kind of regression this test exists to catch, and it did. This report documents the real, live evidence, now that the Day 2 Docker fix (DEF-M2-014) made it possible to actually run the backend for the first time.

## How this was executed

`docker-compose.dev.yml`'s stack was brought up clean (see [milestone2_day2_docker_dev_stack.md](../day2/milestone2_day2_docker_dev_stack.md)) and every M1 + M2 contract endpoint (Section 7 of the SRS) was hit directly with `curl` against the live backend at `http://localhost:8000`, first via the **documented contract path**, then via the **actual (buggy) live path**, to separate "is the underlying logic broken" from "is only the routing broken."

## M1 Regression — Auth

| Check    | Contract path (`/api/v1/auth/...`)               | Actual live path (no prefix)                                        |
| -------- | ------------------------------------------------ | ------------------------------------------------------------------- |
| Register | `POST /api/v1/auth/register` → **404 Not Found** | `POST /register` → **201 Created**, ~2.0s (bcrypt cost, acceptable) |
| Login    | (blocked by register)                            | `POST /login` → **200 OK**, returns valid JWT                       |

**Verdict: FAIL against contract.** The underlying auth logic works correctly — this is purely DEF-M2-002 (missing prefix). But "the feature works if you know the undocumented URL" is not a pass; any client built against the documented contract (including this project's own frontend, once DEF-M2-015 is fixed) gets a 404.

## M1 Regression — Traffic Monitoring

| Check | Contract path                        | Actual live path                                                              |
| ----- | ------------------------------------ | ----------------------------------------------------------------------------- |
| Live  | `GET /api/v1/traffic/live` → **404** | `GET /api/v1/traffic/traffic/live` → **200 OK**, 0.21s, correct payload shape |

**Verdict: FAIL against contract**, same pattern — DEF-M2-003 double-prefix. Underlying data/logic is correct.

## M2 New Services — smoke-tested now that the backend runs

| Service                                    | Endpoint                                                                                                                                                                                                                                                                                                                                                                                          | Result                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Historical Data (FR-01)                    | `/traffic/history`, `/traffic/aggregate`, `/traffic/road-condition/{id}`                                                                                                                                                                                                                                                                                                                          | **404 on every path tried, contract or otherwise** — confirmed these are not implemented anywhere in this gateway. Intern 2's service (`Data/M2_Day6_Traffic_Monitoring_/`) implements all three correctly and passes 35/35 of her own tests, but is not merged into `backend/app/`, so it's unreachable from here. |
| Prediction — congestion (FR-02)            | Contract: `GET /predict/congestion?road_id=...` → **405 Method Not Allowed** (it's a POST). Actual: `POST /api/v1/predict/congestion` with body `{vehicle_count, density, avg_speed_kmph, road_capacity, road_length_km, road_id, hour, day_of_week, is_weekend}` → **422** until all 9 fields are supplied (previously under-documented in DEF-M2-005 — now confirmed the full required schema). |
| Prediction — peak-hours / delay (FR-03/04) | `/predict/peak-hours`, `/predict/delay`                                                                                                                                                                                                                                                                                                                                                           | **404 on every path** — not implemented at all, confirmed.                                                                                                                                                                                                                                                          |
| Route Analysis — optimize (FR-06)          | Contract path: 404 (DEF-M2-004). Actual path `/api/v1/route/api/v1/route/optimize`, **unauthenticated: 401** (endpoint correctly requires a Bearer token via `get_current_user`). **Authenticated with a real token from the login above: 200 OK**, real OSM-resolved path geometry, `distance_km: 7.5`, `congestion_score: 1.2`, `generated_by: "model-v1"`.                                     |

### Latency note (partial Day 4 sanity-check, done here since it's directly relevant)

First authenticated call to `route/optimize` took **5+ seconds and timed out** (cold start — likely first external OpenStreetMap lookup). The immediate retry succeeded in **0.93s**, within the SRS's ~1–2s target. Worth flagging to Intern 1: cold-start latency on the maps wrapper should be checked (e.g. a warm-up call on startup, or basic caching) so the very first user request after a deploy doesn't appear to hang.

## New defect from this session

**DEF-M2-015 (High)**: `Front-end (2)/Front-end/api.js` hardcodes `BASE_URL: 'http://localhost:8001/api/v1'`, but the real backend runs on port **8000** (confirmed in both compose files). This means **even after every routing/contract defect above is fixed, the frontend will never talk to the real backend** — it will keep silently using mock fallback data forever, because it's pointed at the wrong port entirely. This is independent of DEF-M2-002/003/004 and would have quietly blocked Day 5's real integration cycle even in a world where those three were already fixed. Logged in [defect_tracker.md](../day1/defect_tracker.md).

## Regression Summary Table

| Feature                                      | Status                                                                                                                          |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Auth (M1)                                    | **FAIL** — DEF-M2-002 (logic correct, routing broken)                                                                           |
| Traffic Monitoring (M1)                      | **FAIL** — DEF-M2-003 (logic correct, routing broken)                                                                           |
| Historical Data (M2, FR-01)                  | **FAIL** — not integrated (separate unmerged service)                                                                           |
| Prediction — congestion (M2, FR-02)          | **FAIL** — contract mismatch, DEF-M2-005                                                                                        |
| Prediction — peak-hours/delay (M2, FR-03/04) | **FAIL** — not implemented                                                                                                      |
| Route Analysis — optimize (M2, FR-06)        | **PASS at the logic level** once routed around DEF-M2-004 and authenticated — genuinely working code once you get past the bugs |
| Frontend ↔ Backend connectivity              | **FAIL** — DEF-M2-015, wrong port, independent of all of the above                                                              |

## Overall Status

Day 6's regression half is **done as an activity** (executed for real, against a live backend, for the first time this milestone) with an honest result of **FAIL**. This is the correct and expected outcome given DEF-M2-002 through 005 and DEF-M2-015 are all still open — a regression report's job is to catch exactly this, and it did. One piece of good news buried in the failures: the actual business logic for auth, traffic, and route optimization is correct where it's been reached — every failure found is a routing/config/integration problem, not broken feature logic. Once DEF-M2-002, 003, 004, 005, and 015 are fixed, and Intern 2's service is merged in, this same test pass should be re-run and is likely to go green quickly.

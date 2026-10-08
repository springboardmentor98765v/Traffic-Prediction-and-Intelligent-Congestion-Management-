# Day 5: Full Integration Test Cycle (Auth, Monitoring, Prediction, Frontend)

**Executed:** 2026-10-02 · **Environment:** local `docker-compose.dev.yml` (Docker Desktop) · **No deployment**

## 1. Stack under test

`day5_stack_status.txt`:

| Container                   | Status    | In M1 scope         |
| --------------------------- | --------- | ------------------- |
| trafficvision-postgres-dev  | healthy   | yes                 |
| trafficvision-redis-dev     | healthy   | yes                 |
| trafficvision-backend-dev   | healthy   | yes (gateway :8000) |
| trafficvision-ai-dev        | healthy   | yes (stub :8010)    |
| trafficvision-analytics-dev | unhealthy | no (Milestone 3)    |

Postgres held 4,032 `traffic_readings` rows, and `/traffic/live` served them, not the built-in sample feed. For example, R001 had 34 vehicles on the live stack versus 28 in the sample.

## 2. Live end-to-end check: `m1_live_stack_check.py`

**Evidence:** `day5_live_stack_output.txt`, run with a provisioned QA operator account.

| Step                                             | Result    |
| ------------------------------------------------ | --------- |
| Gateway `/health`                                | PASS      |
| Register a new public user → 201                 | PASS      |
| Login → tokens                                   | PASS      |
| `/auth/me` → PUBLIC                              | PASS      |
| `/auth/refresh` → 200                            | PASS      |
| `/traffic/live` → 6 roads                        | PASS      |
| `/traffic/road/R001` → 200                       | PASS      |
| `/traffic/density` → 200                         | PASS      |
| Gateway `/predict/congestion` → 200 (`model-v1`) | PASS      |
| AI Engine stub → `generated_by: heuristic-v0`    | PASS      |
| RBAC: public `POST /alerts/` → 403               | PASS      |
| Operator login → 200                             | PASS      |
| RBAC: operator `POST /alerts/` → 201             | PASS      |
| **Total**                                        | **13/13** |

### First attempt failed (DEF-M1-005, now closed)

The first run gave 10/11. The AI Engine stub returned **503 "Traffic Monitoring service is unavailable"**.

- **Root cause:** `trafficvision-ai-dev` was created on 2026-09-28. `TRAFFIC_API_URL=http://backend:8000/api/v1/traffic/live` was added to `docker-compose.dev.yml` on 2026-09-30, and `docker exec … printenv` showed the variable missing in the container. The stub fell back to `127.0.0.1:8000`, which inside the container points at itself.
- **Fix:** `docker compose -f docker-compose.dev.yml up -d --no-deps ai` (container recreated; no data volumes touched). The re-run passed 13/13.

## 3. Browser end-to-end (Playwright, real Login form, all 3 roles)

**Command:** `M3_OUT_DIR=QA/milestone1/day5/ui python QA/milestone3/day5/frontend_e2e.py`
**Evidence:** `ui/frontend_e2e_output.txt`, `ui/frontend_e2e_results.md`, `ui/screenshots/*.png`

Milestone 1 checks from that journey:

| Check                                                 | Public | Operator | Admin |
| ----------------------------------------------------- | ------ | -------- | ----- |
| UI login lands on the role's dashboard                | PASS   | PASS     | PASS  |
| Session holds a real JWT (not a mock token)           | PASS   | PASS     | PASS  |
| Public user opening the admin dashboard is redirected | PASS   | n/a      | n/a   |

The journey has 31 checks in total: 27 pass and 4 fail. All 4 failures are Milestone 3 features: the Analytics page on :8001 (the analytics container is unhealthy) and one Alerts-page list check. They are tracked under the Milestone 3 QA and are not M1 blockers.

**Live data on screen (FR-08):** the operator dashboard (`ui/screenshots/operator_01_dashboard.png`) shows "179 active vehicles" and "8.24 veh/km network average". `GET /traffic/density` returned `total_vehicle_count: 179` and `average_density: 8.24` at the same time, so the dashboard is driven by the real backend and not mock data. The prediction panel shows "Model-v1", the M2 model that replaced the M1 stub on the gateway.

## 4. In-process integration suite (CI-runnable)

**Command:** `python -m pytest -v -rxX QA/milestone1/tests` · **Evidence:** `day5_integration_output.txt`

**76 passed, 5 xfailed** (each xfail is a logged defect). This includes Monitoring → Prediction: the stub's HTTP call is routed to the in-process gateway's `/traffic/live`, and its output is checked for every road (TC-PRED-03).

## 5. RBAC end-to-end verdict

| Rule                                                        | Verified                         |
| ----------------------------------------------------------- | -------------------------------- |
| Public sign-up cannot create Admin / Operator               | ✅ in-process and live           |
| JWT `role` claim drives `/me` and the frontend landing page | ✅                               |
| Role-gated route: Public 403, Operator / Admin 201          | ✅ in-process and live           |
| Forged or expired tokens rejected                           | ✅                               |
| Frontend page guards redirect the wrong role                | ✅ browser                       |
| Monitoring / prediction routes protected                    | ❌ open to everyone (DEF-M1-003) |

## 6. Defects from this cycle

| ID         | Title                                                        | Sev  | Status |
| ---------- | ------------------------------------------------------------ | ---- | ------ |
| DEF-M1-005 | Stale `ai` container without `TRAFFIC_API_URL`               | High | Closed |
| DEF-M1-008 | Frontend silently swaps in a client-side prediction on error | Low  | Open   |

Prioritized backlog for Day 6: DEF-M1-001 (High) → DEF-M1-003 → DEF-M1-002 → DEF-M1-008 → DEF-M1-004.

# Milestone 3 — Day 6 Regression Report (Intern 5)

Date: 2026-09-25 · Scope: every Milestone 1 & 2 feature, re-tested on the integrated Milestone 3
build · Environment: `docker-compose.dev.yml` (gateway + Alerts :8000, Analytics :8001,
TimescaleDB, Redis; 4-week dataset) · Frontend: `Front end/Front-end` in Edge 153 via Playwright

## Verdict: ⚠️ Mostly stable, but 1 new High regression

**46 of 53 checks pass. All 7 failures are logged with a defect ID.**

- **M1 has no regressions.** Auth, RBAC, monitoring, login and role routing all pass.
- **M2 has no regressions in** Prediction, Route UI and Maps.
- **One real regression was introduced by M3:** the operator dashboard is broken (DEF-M3-023, High).
- **Two older M2 gaps** were found now that the M2 endpoints can finally be reached through the
  gateway: history/aggregate filters are ignored (DEF-M3-022), and `/route/alternate` returns 500
  when OSRM is down (DEF-M3-004).

## Checkpoints (SRS Day 6)

- [x] **Milestone 1 & 2 features re-tested (regression).** All 32 Milestone 2 test cases
      (`QA/milestone2/day2/milestone2_test_cases.md`) plus 10 M1 API checks, 4 M1 UI checks and 1
      new operator-dashboard check, automated in `regression_m1_m2.py`. Run 3 times with identical
      results.
- [x] **Code-quality check run on new code.** See `m3_day6_code_quality_report.md`.
- [ ] **Confirmed system is stable.** Not yet: DEF-M3-023 breaks the operator dashboard. It's a
      one-character fix (Intern 4).

## 1. Results by area

| Area                                    | Pass      | Failures                 | Notes                                                                                                                                            |
| --------------------------------------- | --------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| M1 Auth (API)                           | 6/6       | –                        | register, login, `/me`, refresh, wrong password, no token                                                                                        |
| M1 Monitoring (API)                     | 4/4       | –                        | live (6 roads), road detail, density, unknown road → 404                                                                                         |
| M1 UI (REG-001…003)                     | 4/4       | –                        | login lands user/operator/admin on the right dashboard; live feed shows 6 roads                                                                  |
| M2 Historical (HIST-001…006)            | 3/7       | HIST-002, 004, 005, 005b | **DEF-M3-022**: history ignores the time window, aggregate ignores every filter, unknown road → `200 []`                                         |
| M2 Prediction (PRED-001…007)            | 7/7       | –                        | levels, `model_version`, confidence 0–1, peak hours, delay, invalid road → 404, max latency 416 ms (6 roads)                                     |
| M2 Route API (ROUTE-001…006 + no-token) | 6/7       | ROUTE-002                | **DEF-M3-004**: `/alternate` 500 when OSRM unreachable (still open from Day 2)                                                                   |
| M2 Route UI (ROUTE-007…009)             | 3/3       | –                        | 3 route cards + ETA/distance KPIs; Eco mode; forecast horizon 0 → 60 min updates cards                                                           |
| M2 Maps (MAP-001…006)                   | 6/6       | –                        | live map tiles + 12 road layers, R001 modal with AI prediction, route drawn, label matches card, OSM/Terrain, heatmap toggle                     |
| M2 Frontend (FE-M2-001…007)             | 6/7       | FE-M2-005                | no JS errors on route page, chart painted, ETA updates, conditions panel correct, backend-down fallback. **Download report broken (DEF-M3-023)** |
| Operator dashboard (REG-004, new)       | 0/1       | REG-004                  | **DEF-M3-023**: KPIs stuck on placeholders, JS error `Unexpected end of input`                                                                   |
| Integration (INT-001)                   | 1/1       | –                        | Auth → Live → Prediction (busiest road R005) → Route, route bound to the user                                                                    |
| **Total**                               | **46/53** | **7**                    |                                                                                                                                                  |

Also re-confirmed on Day 6: the full `pytest -q` suite (50 passed, 0 failed), the stack smoke test
(33/34, only DEF-M3-004) and Intern 2's own suite (49/49).

## 2. Regression found: operator dashboard broken by an M3 edit (DEF-M3-023, High)

- **What users see:** the operator dashboard stays on "--%", "Analyzing…" and "Calculating
  real-time delay estimates…". The peak-hour chart is empty and **Download Prediction Report does
  nothing** (`screenshots/reg_06_operator_dashboard.png`).
- **Root cause:** `operator dashboard.html:583`. `handleDownloadReport()` lost the `}` that closes
  it after its `finally` block. So the whole 326-line inline script doesn't parse, and none of
  its functions (`loadOperatorDashboardData`, `renderDelayEstimates`, `renderPeakHourChart`, …)
  exist.
- **Why it's a regression:** the 2026-09-24 copy (`backend (1)/.../Front-end/operator
dashboard.html`) has the brace. The M3 change that added the "Historical Report (CSV)" button
  removed it.
- **Why nothing caught it:** ESLint only reads `.js` files, and this error is inside an HTML page.
  QA added `QA/tools/check_inline_js.js` to CI, so this class of bug now fails the build.
- **Fix (Intern 4):** add `}` after line 582.

## 3. M2 gaps now visible (DEF-M3-022, Medium)

The M2 history/aggregate endpoints returned 404 through the gateway for all of Milestone 2, so
they were never functionally tested. Now they respond, but:

| Call                                                                         | Expected            | Actual                     |
| ---------------------------------------------------------------------------- | ------------------- | -------------------------- |
| `/traffic/aggregate?road_id=R001&start_time=…&end_time=…`                    | R001 only, in range | all 6 roads, whole dataset |
| `/traffic/history?road_id=R001&start_time=2026-08-01T00:00&end_time=…T05:00` | ≤ 6 rows            | 500 rows (= `limit`)       |
| `/traffic/history?…&start_time > end_time`                                   | 400                 | 200                        |
| `/traffic/history?road_id=R999`                                              | 404                 | `200 []`                   |

Cause: `app/services/traffic_service.py`. The history query never adds the time filters, and
the aggregate query is a fixed `GROUP BY road_id` that ignores all parameters.

## 4. Compared with the Milestone 2 Day 6 regression

| Feature                                   | M2 Day 6 (Milestone 2)                 | M3 Day 6 (now)                                          |
| ----------------------------------------- | -------------------------------------- | ------------------------------------------------------- |
| Auth (M1)                                 | ❌ contract paths 404                  | ✅                                                      |
| Traffic Monitoring (M1)                   | ❌ double prefix 404                   | ✅                                                      |
| Historical data (M2)                      | ❌ not integrated (404)                | ⚠️ reachable, filters ignored (DEF-M3-022)              |
| Prediction congestion / peak / delay (M2) | ❌ contract mismatch / not implemented | ✅                                                      |
| Route optimize (M2)                       | ⚠️ wrong path                          | ✅ (alternate ❌ DEF-M3-004)                            |
| Frontend ↔ backend (M2)                   | ❌ wrong port                          | ✅ for M1/M2 pages (Analytics page still ❌ DEF-M3-013) |

Milestone 2's regression failures have been fixed. The remaining problems are listed above.

## 5. Fixes needed before Day 7 sign-off (regression part)

| Defect                   | Owner                     | Fix                                                                                                                             |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| DEF-M3-023 (High)        | Intern 4 (Frontend)       | add the missing `}` at `operator dashboard.html:583`                                                                            |
| DEF-M3-022 (Medium)      | Intern 2 (Data) / backend | apply `road_id`, `start_time`, `end_time` (+ `interval`) in history/aggregate SQL; 404 for unknown road, 400 for inverted range |
| DEF-M3-004 (Medium/High) | Backend                   | fallback or 503 in `/route/alternate`                                                                                           |

## Reproduce

```
docker compose -f docker-compose.dev.yml up -d
python QA/milestone3/day6/regression_m1_m2.py     # ~3 min, API + Edge; writes regression_results.md
```

Evidence: `regression_results.md` / `.json`, `regression_output.txt`, `screenshots/reg_01…06`.

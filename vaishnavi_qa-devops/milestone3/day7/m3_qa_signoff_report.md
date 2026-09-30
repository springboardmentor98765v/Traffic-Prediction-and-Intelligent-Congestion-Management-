# Milestone 3 — QA Sign-off Report

Project: TrafficVision AI · Milestone 3 (Alerts, Analytics, AI Insights)
Prepared by: Intern 5 (QA, DevOps & Release Engineering) · Date: 2026-09-25
Build tested: `Team-1` working tree as of 2026-09-25, local `docker-compose.dev.yml` stack
(gateway + Alert Service :8000, Analytics :8001, TimescaleDB, Redis; 4-week dataset, 6 roads)

---

## Verdict: ❌ NOT SIGNED OFF (No-Go)

**What works:** Milestone 1 & 2 features have no regressions. The Alert Service delivers alerts
reliably, and the Analytics numbers are accurate and fast.

**Why it can't be signed off:**

- **6 High-severity defects are still open.** Team rule (`docs/QUALITY-GATES.md`): "No critical
  or high-severity defects remain open."
- **Alert RBAC** isn't enforced by the server.
- **The frontend can't load Analytics data:** it now calls the right service, but Analytics has no CORS (DEF-M3-014).
- **The AI Insights service doesn't exist.**
- **The operator dashboard is broken** by an M3 edit (DEF-M3-023, found in the Day 6 regression).

None of the fixes requested on Day 5 had landed by the time of this run.

Sign-off will be re-issued when the exit criteria in §6 are met. Re-running the final cycle takes
about 10 minutes (§8).

---

> **Retest update (2026-09-25, Intern 4 frontend):** DEF-M3-013 fixed on the frontend side (waiting on DEF-M3-014 CORS), DEF-M3-018 and DEF-M3-019 closed, **DEF-M3-023 still open**. Verdict unchanged: **Not signed off.** Details: `../retest_frontend_2026-09-25/frontend_retest_report.md`.

> **Full retest 2026-09-26 (Data + Frontend + Backend updates):** 7 defects closed
> (DEF-M3-004, 009, 010, 011, 012, 013, 014). **2 new High:** DEF-M3-024 (public users see
> Critical alerts) and DEF-M3-025 (automatic alert producers rejected with 401, no alerts
> created). Still open High: DEF-M3-005 (partly), 017, 021, 023. **14 open (6 High).**
> Verdict unchanged: **Not signed off.** Details: `../retest_2026-09-26/retest_report.md`.
> The tables below are the Day 7 snapshot.

## 1. Day 7 checkpoints

- [x] **Final full test cycle completed:** smoke, integration, RBAC, notification reliability,
      failure-mode (Redis down), and frontend E2E in a real browser for all 3 roles (§3).
- [x] **QA sign-off report written:** this document.
- [x] **Deployment Readiness Checklist written:** `deployment_readiness_checklist_M4.md`,
      marked **"Planning only — for Milestone 4 use"**. No deployment activity was performed.

## 2. SRS §12.2 integration checkpoints

| Checkpoint            | Due       | Status        | Notes                                                                                                                                                                           |
| --------------------- | --------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract Freeze       | Day 2 EOD | ⚠️ Partly met | Alerts frozen Day 2. Analytics frozen late (2026-09-25, Intern 2). AI Insights never frozen (no service)                                                                        |
| First Vertical Slice  | Day 4     | ⚠️ Partly met | Congestion and accident alerts reach the frontend **bell** end-to-end (61 ms). Not the Alerts page list (DEF-M3-018), and not Critical alerts for operators/admins (DEF-M3-012) |
| Full Integration      | Day 5     | ❌ Not met    | Analytics unreachable from UI (DEF-M3-013/014). AI Insights missing (DEF-M3-017)                                                                                                |
| Regression & Sign-off | Day 7     | ❌ Not met    | Regression 46/53 (operator dashboard broken, DEF-M3-023); 6 High defects open                                                                                                   |

## 3. Final validation cycle results (2026-09-25)

| #   | Suite                                                                    | Command                          | Result                                                                                                                              | Evidence                                  |
| --- | ------------------------------------------------------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | Automated suite (M1/M2 regression, backend tests, M3 Alerts + Analytics) | `python -m pytest -q`            | **50 passed, 11 xfailed, 0 failed.** The 11 xfails are known open defects, automated as strict xfails                               | `pytest_output.txt`, `pytest_junit.xml`   |
| 2   | Full-stack smoke (M1 + M2 + M3 Alerts)                                   | `stack_smoke_test.py`            | **33 / 34.** Only failure: `/route/alternate` 500 (DEF-M3-004)                                                                      | `smoke_output.txt`                        |
| 3   | Notification reliability                                                 | `alert_delivery_check.py -n 100` | **100/100 delivered, 0 lost, p50 81 ms, p95 213 ms, max 395 ms** (target p95 < 1 s). Watcher dedup ✅. Detector → accident alert ✅ | `alert_reliability_output.txt`            |
| 4   | Integration cycle, 3 real accounts                                       | `integration_cycle.py`           | **31 pass · 11 fail · 2 blocked** (same as Day 5)                                                                                   | `integration_results.md`                  |
| 5   | Frontend E2E in Edge, 3 roles                                            | `frontend_e2e.py`                | **17 pass · 14 fail** (same as Day 5)                                                                                               | `frontend_e2e_results.md`, `screenshots/` |
| 6   | Analytics performance + Redis-down                                       | `analytics_perf_cache_check.py`  | Performance ✅ (cold ≤ 0.4 s, warm ~50 ms, index scans). **Redis down: trends/heatmap hang > 90 s ❌ (new DEF-M3-020)**             | `analytics_perf_redis_down_output.txt`    |
| 7   | Gateway with Redis down                                                  | inline probe                     | ✅ health, traffic, road, predict, alert create, alert list all 200/201                                                             | `gateway_redis_down_output.txt`           |
| 8   | M1/M2 regression (Day 6), API + Edge                                     | `regression_m1_m2.py`            | **46 / 53.** Fails: DEF-M3-022 ×4 (history/aggregate filters), DEF-M3-004, DEF-M3-023 ×2 (operator dashboard)                       | `../day6/regression_results.md`           |

### RBAC results (final)

| Check                                                           | Expected | Actual              |               |
| --------------------------------------------------------------- | -------- | ------------------- | ------------- |
| Login lands each role on its own dashboard (UI)                 | yes      | yes                 | ✅            |
| Public user blocked from admin dashboard (UI)                   | yes      | yes                 | ✅            |
| Self-registration with `role: admin` gives PUBLIC               | yes      | yes                 | ✅            |
| Route analysis requires a token                                 | 401      | 401                 | ✅            |
| Critical alert hidden from public user                          | hidden   | hidden              | ✅            |
| Critical alert visible to operator / admin (as the UI calls it) | visible  | **hidden**          | ❌ DEF-M3-012 |
| Accident alert hidden from public user                          | hidden   | **visible**         | ❌ DEF-M3-007 |
| Public user + `?role=admin` sees Critical                       | no       | **yes**             | ❌ DEF-M3-005 |
| Alerts list / create / mark-read without a token                | 401      | **200 / 201 / 200** | ❌ DEF-M3-005 |

## 4. Feature status

| Area                  | Status                  | Summary                                                                                                                                                                                                                                                |
| --------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| M1 Auth + RBAC        | ✅ Stable               | Register, login, refresh, `/me`, role routing, domain allow-list: no regressions                                                                                                                                                                       |
| M2 Traffic Monitoring | ⚠️                      | Live, road, density ✅; data consistent with Analytics ✅; history/aggregate filters ignored (DEF-M3-022)                                                                                                                                              |
| M2 Prediction         | ✅ Stable               | All 6 roads, peak hours, delay                                                                                                                                                                                                                         |
| M2 Route Analysis     | ⚠️                      | optimize / travel-time / conditions ✅; `/alternate` 500 when OSRM is down (DEF-M3-004)                                                                                                                                                                |
| M3 Alert Service      | ⚠️ Works, insecure      | Create/list/read ✅. Congestion watcher: 672 real readings → exactly 30 alerts ✅. Delivery p95 213 ms ✅. Server-side RBAC ❌                                                                                                                         |
| M3 Analytics          | ⚠️ Works, not connected | Trends/heatmap exact vs raw data ✅, CSV ✅, cache ✅, < 0.4 s ✅. Input validation, IST reports, CORS, Redis-down ❌ (fixes in progress by Intern 2)                                                                                                  |
| M3 AI Insights        | ❌                      | Anomaly detector (library) works ✅. Recommendations service not delivered ❌                                                                                                                                                                          |
| M3 Frontend           | ❌                      | Login, role dashboards, route, maps, bell use live APIs ✅. **Operator dashboard broken by an M3 edit (DEF-M3-023)**. Analytics page and AI panel show mock data; Alerts list not from Alert Service                                                   |
| Code quality (Day 6)  | ⚠️                      | New M3 Python: 48 flake8 findings, all cosmetic, no logic findings. Frontend: 1 syntax error (DEF-M3-023), 4 real ESLint errors. Alerts and AI detector have no owner unit tests. QA-owned code is clean. See `../day6/m3_day6_code_quality_report.md` |

## 5. Open defects at sign-off

Full details: `QA/milestone3/day1/defect_tracker.md`. Closed this milestone: DEF-M2-006,
DEF-M2-012, DEF-M2-013, DEF-M3-001, 002, 003, 015, 018, 019. Fixed, pending end-to-end retest: DEF-M3-013 (needs DEF-M3-014).

| Defect                                                                                                    | Severity / Priority            | Owner                          | Status          |
| --------------------------------------------------------------------------------------------------------- | ------------------------------ | ------------------------------ | --------------- |
| **DEF-M3-005** Alert endpoints have no JWT check                                                          | **High** / High                | Intern 1 (Backend / Team Lead) | Open            |
| **DEF-M3-012** Operators/admins never see Critical alerts                                                 | **High** / High                | Intern 1                       | Open            |
| **DEF-M3-014** Analytics has no CORS                                                                      | **High** / High                | Intern 2                       | In Progress     |
| **DEF-M3-017** AI Insights service not delivered                                                          | **High** / High                | Intern 3 (AI)                  | Open            |
| **DEF-M3-021** JWT signing secret hard-coded (new, Day 7)                                                 | **High** / Medium (M4 blocker) | Intern 1                       | Open            |
| **DEF-M3-023** Operator dashboard script broken: KPIs, charts, report download (M3 regression, new Day 6) | **High** / High                | Intern 4                       | Open            |
| DEF-M3-004 `/route/alternate` 500 when OSRM down                                                          | Medium / High                  | Backend                        | Open            |
| DEF-M3-009 Malformed date → 500                                                                           | Medium / High                  | Intern 2                       | In Progress     |
| DEF-M3-020 Analytics hangs > 90 s when Redis is down (new, Day 7)                                         | Medium / High                  | Intern 2                       | Open            |
| DEF-M3-007 Accident alerts visible to public users                                                        | Medium / Medium                | Intern 1 + 3                   | Open (decision) |
| DEF-M3-010 Report days in UTC vs IST charts                                                               | Medium / Medium                | Intern 2                       | In Progress     |
| DEF-M3-022 History/aggregate filters ignored (new, Day 6)                                                 | Medium / Medium                | Intern 2 / backend             | Open            |
| DEF-M3-008 "Severe" outside severity vocabulary                                                           | Low / Medium                   | Intern 1 + 2                   | Open            |
| DEF-M3-011 Unknown road / inverted range → 200 empty                                                      | Low / Medium                   | Intern 2                       | In Progress     |
| DEF-M3-016 Timestamps without timezone                                                                    | Low / Medium                   | Intern 1                       | Open            |
| DEF-M2-008 scikit-learn not pinned                                                                        | Low / Medium                   | AI                             | Open            |
| DEF-M2-011 Dead auth/src code                                                                             | Low / Low                      | Backend                        | Open            |
| DEF-M3-006 AVG HTTPS scanning (QA machine only)                                                           | Low / Medium                   | QA machine owner               | Open (env)      |

**Totals:** 18 open. By severity: 6 High, 6 Medium, 6 Low. By status: 14 Open, 4 In Progress.

## 6. Exit criteria for QA sign-off

1. DEF-M3-005 and DEF-M3-012 fixed (role taken from the JWT), and the 5 strict xfails in
   `test_alerts_api.py` turned into passing tests.
2. DEF-M3-014 fixed (DEF-M3-013 already fixed): the Analytics page loads live data from :8001 in the browser
   E2E for all 3 roles.
3. DEF-M3-023 fixed: the operator dashboard loads and the report downloads (REG-004 and
   FE-M2-005 pass in `regression_m1_m2.py`; `check_inline_js.js` passes).
4. DEF-M3-017: AI recommendations endpoint delivered and contract frozen, **or** formally
   descoped to Milestone 4 by the Team Lead (then recorded here as an accepted exception).
5. DEF-M3-021 fixed or formally accepted as a Milestone 4 blocker by the Team Lead (no
   deployment happens in M3).
6. No new High defects in the re-run. Medium defects are accepted only with a named owner and
   target in the Milestone 4 backlog.
7. `python -m pytest -q` still 0 failed, smoke ≥ 34/34 (or DEF-M3-004 accepted), and alert
   delivery p95 < 1 s.

## 7. Sign-off

| Role                 | Name | Decision                                    | Date       |
| -------------------- | ---- | ------------------------------------------- | ---------- |
| QA (Intern 5)        |      | ❌ Not signed off: exit criteria §6 not met | 2026-09-29 |
| Team Lead (Intern 1) |      |                                             |            |

## 8. How to re-run the final cycle (≈ 10 min)

```
docker compose -f docker-compose.dev.yml up -d
bash QA/milestone3/day6/analytics_setup.sh                       # one-time data load
python -m pytest -q
python QA/milestone3/day2/stack_smoke_test.py
python QA/milestone3/day4/alert_delivery_check.py -n 100
M3_OUT_DIR=QA/milestone3/day7 python QA/milestone3/day5/integration_cycle.py
M3_OUT_DIR=QA/milestone3/day7 python QA/milestone3/day5/frontend_e2e.py
python QA/milestone3/day6/regression_m1_m2.py                  # M1/M2 regression, ~3 min
python QA/milestone3/day6/analytics_perf_cache_check.py         # stops Redis briefly
```

Every failing check names its defect ID, so a fixed defect shows up as a pass, or as an XPASS
in pytest to be promoted.

## QA Retest Addendum — 2026-09-29

**Decision remains NO-GO.** The local root suite had 27 passed, 46 skipped, and 0 failed. The backend suite passed 9/9, the Data suite 60/60, watcher tests 7/7, and inline JavaScript parsed in all eight current frontend HTML files. QA configuration and the backend route test fixture were repaired; targeted Black/Flake8 checks passed.

The Docker engine was unavailable (`docker compose ps` could not connect to the Docker Desktop Linux engine pipe). Fresh checks to ports 8000, 8001, and 8010 were refused. Therefore the API integration cycle, stack smoke, alert delivery, real-browser E2E, full M1/M2 regression, and Redis-down performance check were not rerun. The 46 service-dependent skips are not passes. The 2026-09-28 full-stack results remain the latest integrated evidence until a new live-stack run is completed. See [the 2026-09-29 QA retest](../retest_2026-09-29/qa_retest_report.md).

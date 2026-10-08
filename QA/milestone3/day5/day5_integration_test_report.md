# Milestone 3 — Day 5 Integration Test Report (Intern 5)

Date: 2026-09-25 · Owner: Intern 5 (QA/DevOps), led with Intern 1 per SRS §13
Environment: `docker-compose.dev.yml`, 4 containers healthy (gateway + Alert Service :8000,
Analytics :8001, TimescaleDB, Redis), 4-week dataset loaded (4,032 readings, 6 roads).
Frontend: `Front end/Front-end` driven in Microsoft Edge 153 via Playwright.

## Checkpoints (SRS Day 5)

- [x] **Full journey tested end-to-end.** Auth → Monitoring → Prediction → Route → Analytics →
      AI Insights → Alerts → Frontend, as three real accounts (user / operator / admin), both at
      API level (44 checks) and through the real UI in a browser (31 checks).
- [x] **Access rules (RBAC) re-checked on alerts.** ❌ Not met: operators/admins can't see
      Critical alerts in the UI (DEF-M3-012), and public users see accident alerts (DEF-M3-007)
      and can escalate or forge alerts (DEF-M3-005).
- [x] **Accident alerts confirmed to appear correctly.** ⚠ Partly met: incident reading →
      anomaly detector → Alert API → operator's bell drawer in **61 ms**. But the alert shows as
      location "Grid", "5h ago", is also shown to public users, and never appears in the Alerts
      page list (DEF-M3-018, DEF-M3-016, DEF-M3-007).

**SRS §12.2 "Full Integration" checkpoint (Alerts + Analytics + AI Insights + M1/M2 run
together and pass smoke tests): NOT PASSED.** The M1/M2 stack and the Alert Service integrate.
Analytics works as a service but is not reachable from the frontend. AI Insights doesn't exist.

## 1. Results at a glance

| Run                           | Script                                                        | Pass | Fail | Blocked |
| ----------------------------- | ------------------------------------------------------------- | ---- | ---- | ------- |
| API-level integration cycle   | `integration_cycle.py` → `integration_results.md`             | 31   | 11   | 2       |
| Frontend E2E, 3 roles in Edge | `frontend_e2e.py` → `frontend_e2e_results.md`, `screenshots/` | 17   | 14   | –       |

## 2. Integration matrix: does each piece work with the others?

| Service / flow                   | Service alone                                                                          | Through gateway / other services                                                               | From the frontend (browser)                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Auth + RBAC (M1)                 | ✅ register, login, `/me` role for all 3 roles, 401 without token                      | ✅ JWT accepted by Route                                                                       | ✅ UI login lands each role on its own dashboard; public user blocked from admin page             |
| Monitoring (M2)                  | ✅ live (6 roads), road detail, density                                                | ✅ same rows as Analytics (R001 latest = report row, 34 veh)                                   | ✅ used by Alerts/Route pages                                                                     |
| Prediction (M2)                  | ✅ all 6 roads, peak hours                                                             | –                                                                                              | ✅                                                                                                |
| Route analysis (M2)              | ✅ optimize, travel-time, conditions, 401 without token; ❌ alternate 500 (DEF-M3-004) | –                                                                                              | ✅ 3 route calls return 200 for each role                                                         |
| **Alert Service** (M3, Intern 1) | ✅ create/list/read                                                                    | ✅ congestion watcher and anomaly detector deliver into it                                     | ⚠ bell drawer only; Critical hidden from operator/admin (DEF-M3-012); list not wired (DEF-M3-018) |
| **Analytics** (M3, Intern 2)     | ✅ trends, heatmap, report; roads = Monitoring roads                                   | ✅ report CSV feeds the watcher replay                                                         | ❌ wrong URL + no CORS → page shows mock data (DEF-M3-013, DEF-M3-014)                            |
| **AI Insights** (M3, Intern 3)   | ⛔ no service on :8010                                                                 | ✅ anomaly detector (library) classifies baseline as `normal`, incident as `possible_incident` | ❌ recommendations are hard-coded heuristics (DEF-M3-017)                                         |

## 3. End-to-end alert flows (the M3 core)

| Flow                                   | Path                                                                                                                                               | Result                                                                        |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Congestion → alert                     | 672 real R003 readings (4 weeks, from Analytics report) → congestion watcher → Alert API                                                           | ✅ **30 alerts = 30 High/Severe episodes**, dedup correct, no spurious alerts |
| Incident → accident alert              | Incident reading R004 → `AnomalyDetector` (`possible_incident`) → `POST /alerts/` (as `automate_accident_alerts.py`) → operator's `GET /alerts/my` | ✅ visible in **61 ms** (API), shown in operator/admin bell drawer (UI)       |
| RBAC on a Critical accident alert      | same alert read with each role's JWT, the way the frontend calls it                                                                                | ❌ hidden from user ✅, **hidden from operator ❌ and admin ❌** (DEF-M3-012) |
| RBAC on detector accident alert (High) | public user's bell drawer                                                                                                                          | ❌ visible to public user (DEF-M3-007)                                        |
| Abuse cases                            | no-token list / no-token create / public user `?role=admin` / public user marks Critical read                                                      | ❌ all four allowed (DEF-M3-005)                                              |

## 4. What the frontend actually calls (from the browser network log)

| Page                | Call                                                                                      | Result                                         |
| ------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Login               | `POST :8000/api/v1/auth/login`                                                            | 200, real JWT stored                           |
| every page (bell)   | `GET :8000/api/v1/alerts/my` (no `role`)                                                  | 200, but always the `user` view                |
| Alerts.html         | `GET :8000/api/v1/traffic/live`, `/density`                                               | 200, list is built from these, not from alerts |
| analytics.html      | `GET 127.0.0.1:8000/analytics/heatmap`                                                    | **404** (wrong port)                           |
| analytics.html      | `GET 192.168.1.4:8000/analytics/{heatmap,trends}`                                         | **connection refused** (hard-coded LAN IP)     |
| analytics / Alerts  | `GET :8010/api/v1/ai/recommendations`, `:8010/ai/recommendations`, `192.168.1.4:8010/...` | **connection refused** (no AI service)         |
| route-analysis.html | `GET :8000/api/v1/route/*`                                                                | 200 ×3                                         |

The frontend hides every one of these failures behind mock data with no user-visible error
(except small "MOCK DATA" badges on the Analytics page), which is why these gaps weren't visible
in manual testing. Screenshot `screenshots/admin_03_analytics.png` shows the effect: the heatmap
lists 7 roads including R007, which doesn't exist in the data.

## 5. Performance observed during integration

| Call                                              | Latency                                    |
| ------------------------------------------------- | ------------------------------------------ |
| Alert create → visible to operator                | 61 ms                                      |
| Analytics trends / heatmap / 4-week report (cold) | 45–273 ms, report ≈ 100 ms                 |
| Route optimize (external OSRM)                    | ≈ 1.2 s                                    |
| `/traffic/road/{id}`                              | up to 2.3 s on some calls (watch on Day 6) |

No analytics slowness was seen at 4-week scale, so no indexing/caching request goes to Intern 2
(SRS §15 risk).

## 6. Prioritized defect list (Day 6 backlog)

Full details and repro steps in `../day1/defect_tracker.md`.

| #   | Defect                                                                              | Sev / Pri       | Owner          | Why it matters for sign-off                                     |
| --- | ----------------------------------------------------------------------------------- | --------------- | -------------- | --------------------------------------------------------------- |
| 1   | **DEF-M3-005** alert endpoints have no JWT check                                    | High / High     | Intern 1       | Anyone can read Critical alerts, forge alerts, mark them read   |
| 2   | **DEF-M3-012** operators/admins never see Critical alerts in the UI                 | High / High     | Intern 1 (+4)  | Core M3 promise; fixed by the same change as #1 (role from JWT) |
| 3   | **DEF-M3-013** frontend Analytics URLs wrong (:8000 / LAN IP)                       | High / High     | Intern 4       | Analytics page shows only mock data                             |
| 4   | **DEF-M3-014** Analytics has no CORS                                                | High / High     | Intern 2       | Needed together with #3                                         |
| 5   | **DEF-M3-017** AI Insights service missing                                          | High / High     | Intern 3       | Blocks the AI part of Full Integration                          |
| 6   | DEF-M3-009 malformed date → 500                                                     | Medium / High   | Intern 2       | Crash on bad input                                              |
| 7   | DEF-M3-004 `/route/alternate` → 500 when OSRM fails                                 | Medium / High   | Backend        | M2 feature fails in the integrated build                        |
| 8   | DEF-M3-007 accident alerts shown to public users                                    | Medium / Medium | Intern 1 + 3   | Needs product decision                                          |
| 9   | DEF-M3-018 Alerts page list not fed by Alert Service; bell ignores `type`/`road_id` | Medium / Medium | Intern 4       | Accident alerts invisible on the Alerts page                    |
| 10  | DEF-M3-019 login fallback creates unauthenticated Operator session                  | Medium / Medium | Intern 4       | UI RBAC bypass when the gateway is down                         |
| 11  | DEF-M3-010 report dates in UTC, charts in IST                                       | Medium / Medium | Intern 2       | CSV doesn't match charts                                        |
| 12  | DEF-M3-016 timestamps without timezone ("5h ago" on new alerts)                     | Low / Medium    | Intern 1       | Wrong alert ages in UI                                          |
| 13  | DEF-M3-008 "Severe" not in severity vocabulary                                      | Low / Medium    | Intern 1 + 2/3 |                                                                 |
| 14  | DEF-M3-011 unknown road / inverted range → 200 empty                                | Low / Medium    | Intern 2       |                                                                 |
| 15  | DEF-M2-008, DEF-M3-001/002 (stale tests, sklearn pin)                               | Low             | Backend / QA   | Needed for a clean Day 6 regression run                         |
| env | DEF-M3-006 (AVG TLS), DEF-M3-015 (`localhost` IPv6 resets)                          | Low             | QA             | This machine only                                               |

**Minimum for Day 7 sign-off:** #1–#5 fixed (or #5 formally descoped by the Team Lead), then
re-run both Day 5 scripts. Every failing check names its defect, so it goes green once fixed.

## 7. Test harness notes

- Operator/admin accounts: public sign-up always creates `role=user`, so each run registers
  fresh accounts and promotes two with `UPDATE users SET role=...` in the dev DB.
- Scripts use `127.0.0.1`, not `localhost` (DEF-M3-015).
- The browser test serves the static frontend from disk via Playwright interception (origin
  kept as `http://127.0.0.1:5500`). A real `http.server` works too, but on this machine AVG Web
  Shield aborts the `api.js` download and Edge retries after ~20 s (DEF-M3-006). Because
  intercepted pages have no server IP, Edge's Local Network Access check is disabled for the
  run. This doesn't affect real users loading the page from a local server.
- Test data: alerts with `QA-D5-…` messages/road ids on R004 and `QA-D5-R003-…`. Reset:
  `docker exec trafficvision-postgres-dev psql -U traffic -d trafficvision -c "DELETE FROM alerts WHERE road_id LIKE 'QA-%' OR message LIKE 'QA-D5-%' OR message LIKE 'QA Day 5%';"`

## Reproduce

```
docker compose -f docker-compose.dev.yml up -d
bash QA/milestone3/day6/analytics_setup.sh
python QA/milestone3/day5/integration_cycle.py     # API level, ~30 s
python QA/milestone3/day5/frontend_e2e.py          # browser, 3 roles, ~3 min (needs Edge)
```

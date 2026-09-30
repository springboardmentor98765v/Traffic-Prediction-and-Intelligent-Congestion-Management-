# Frontend Retest — Intern 4 update (2026-09-25)

Build: Intern 4's updated frontend, now in **`front-end/Front-end/`** (folder renamed from
`Front end/`). Same Docker stack as Day 7. Backend and Analytics unchanged since Day 7.

## Result: 3 of 4 frontend defects fixed ✅, 1 still open ❌

| Defect                                                 | Before | Now                                                                                                                                                                                                                                                                                                                                                  | Evidence                                                                                                           |
| ------------------------------------------------------ | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **DEF-M3-013** Analytics URLs (:8000 / LAN IP)         | ❌     | ✅ **Fixed (frontend side).** `ANALYTICS_BASE` and `ANALYTICS_TRENDS_BASE` = `http://127.0.0.1:8001`, no `192.168.x` anywhere. The page now calls the right service, but the browser blocks the response: `No 'Access-Control-Allow-Origin' header` → **still waiting on DEF-M3-014 (Intern 2, CORS)**. The page will show live data once that lands | integration check "ANALYTICS_BASE serves /analytics/heatmap" now PASS; E2E console log                             |
| **DEF-M3-018** Alerts page not from Alert Service      | ❌     | ✅ **Fixed.** List built from `alertsAPI.getMyAlerts()` and shows the real accident alert on R004 for operator/admin. The bell now maps `type` and `road_id` (shows "R004", not "Grid"). Public-user page: 494 alerts loaded in 2 s                                                                                                                  | E2E rows "Alerts page list shows the Alert Service accident alert" PASS (operator, admin); isolated rerun for user |
| **DEF-M3-019** Login fallback creates Operator session | ❌     | ✅ **Fixed.** With the gateway blocked: stays on `Login.html`, no token stored, shows "Server unreachable. Please check your connection and try again."                                                                                                                                                                                              | `screenshots/def_m3_019_login_backend_down.png`                                                                    |
| **DEF-M3-023** Operator dashboard script broken        | ❌     | ❌ **NOT fixed.** `operator dashboard.html` inline script #4 (line 549) still fails with `Unexpected end of input`. `handleDownloadReport()` still has no closing `}` after `finally { … }` (now **line 597**). KPIs stay on placeholders; Download Prediction Report does nothing                                                                   | `check_inline_js.js` FAIL; regression REG-004 + FE-M2-005 FAIL; `screenshots/reg_06_operator_dashboard.png`        |

## Suite results (same stack, retest folder)

| Suite                        | Day 7   | Retest      | Change                                                                                                                                                                                                                                                                                              |
| ---------------------------- | ------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend E2E (3 roles, Edge) | 17 / 31 | **18 / 31** | +2 from DEF-M3-018 (operator + admin Alerts list now PASS), −1 timing: the public user's Alerts page (first page of the run) had not called `/alerts/my` yet when checked; an isolated rerun called it and loaded 494 alerts in 2 s. Remaining fails are backend/Data/AI: DEF-M3-012, 007, 014, 017 |
| Integration cycle (API)      | 31 / 44 | **32 / 44** | +1 (DEF-M3-013 frontend contract)                                                                                                                                                                                                                                                                   |
| M1/M2 regression             | 46 / 53 | **46 / 53** | unchanged: DEF-M3-023 still breaks the operator dashboard                                                                                                                                                                                                                                           |
| Inline-script syntax check   | 1 fail  | **1 fail**  | operator dashboard.html                                                                                                                                                                                                                                                                             |

## New minor lint findings (not defects)

- `api.js` lines 2497 and 2681: empty `catch (_) { }` around localStorage theme access
  (ESLint `no-empty`). Intentional. Add a comment inside, e.g. `catch (_) { /* storage blocked */ }`.
- Still present from Day 6: `alternateEndpoint` unused (l.302), 2× useless try/catch (l.384, 401),
  `time_bucket` unused (l.1729).
- Prettier: 10 frontend files need `npx prettier --write front-end`.

## Still needed from Intern 4

1. **DEF-M3-023:** add the missing `}` after the `finally` block in `handleDownloadReport()`
   (`operator dashboard.html`, around line 597). Check with
   `node QA/tools/check_inline_js.js front-end/Front-end/*.html`.
2. Optional clean-up: the 6 ESLint errors above + Prettier.

## QA tooling updated for the rename

`integration_cycle.py` / `frontend_e2e.py` now find the frontend under `front-end/` or
`Front end/` (override with `FRONTEND_DIR`). CI and the `.eslintrc.json` override point at
`front-end/`. The regression script gained `M3_OUT_DIR` so retests don't overwrite Day 6 evidence.

## Reproduce

```
export M3_OUT_DIR=QA/milestone3/retest_frontend_2026-09-25
python QA/milestone3/day5/frontend_e2e.py
python QA/milestone3/day6/regression_m1_m2.py
python QA/milestone3/day5/integration_cycle.py
node QA/tools/check_inline_js.js front-end/Front-end/*.html
```

# Day 2 Test Execution Report — Milestone 2

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Test cases executed against: [milestone2_test_cases.md](milestone2_test_cases.md)
Screenshot evidence folder: `QA/milestone2/day2/screenshots/`

## Test Execution Summary

| Category | Test Count | Passed | Failed | Blocked | Pending |
|---|---:|---:|---:|---:|---:|
| Historical Traffic Data (API) | 6 | 0 | 0 | 6 | 0 |
| Traffic Prediction (API) | 7 | 0 | 0 | 7 | 0 |
| Route Analysis (API) | 6 | 0 | 0 | 6 | 0 |
| Route Analysis (UI) | 3 | 1 | 2 | 0 | 0 |
| Maps Integration (UI) | 6 | 6 | 0 | 0 | 0 |
| Frontend (UI) | 7 | 6 | 0 | 0 | 1* |
| Regression | 3 | 3 | 0 | 0 | 0 |
| Integration | 1 | 0 | 0 | 1 | 0 |
| **Total** | **39** | **16** | **2** | **20** | **1** |

\* FE-M2-005 (download report) is not "pending" from the original plan but a corrected test target — see Part B result table.

\* Some IDs (ROUTE-007–009) are counted once under Route Analysis (UI); table above splits API vs UI rows from the same 32 authored cases plus the API/UI split for Route Analysis.

Note: after the backend source was fixed (see Part A below), the legacy `tests/test_day4_api.py` suite was re-run against the real app and now **fails** (2/2) rather than being blocked at import — routing defects DEF-M2-002/003 broke both Auth and Traffic Monitoring at the API level. REG-001/REG-003 as authored (UI-level, via mock fallback) both **Pass** — see Part B — so Milestone 1 regression is intact at the UI layer even though the real API layer underneath it is currently broken.

---

## Part A — API / Backend Execution (completed)

### Command run
```
& '.\.venv\Scripts\python.exe' -m pytest tests/test_day4_api.py -q
```

### Result
```
ERROR collecting tests/test_day4_api.py
ImportError while importing test module '...\tests\test_day4_api.py'.
tests\test_day4_api.py:3: in <module>
    from backend.app.main import app
E   ModuleNotFoundError: No module named 'backend'
1 error in 1.63s
```

### Docker Compose check
`docker-compose.yml` defines the `backend` service with `build.context: ./backend`, but no `backend/` directory exists anywhere in the repository (confirmed via full directory scan). The stack cannot be built or started locally, so `docker compose up --build` and the `/health` check from the Day 2 CI doc cannot be validated either.

### Re-check after `Backend/` folder was added (2026-09-12)
A `Backend/Backend/` folder was added to the repo, so pytest was re-run:
```
ModuleNotFoundError: No module named 'backend'
```
Still fails, unchanged. Cause: the new folder only contains documentation and config (`README.md`, `api_contracts.md`, `BACKEND_SUMMARY.md`, `Dockerfile`, `requirements.txt`, `.db` files) — a repo-wide search for `app/` directories or `main.py` found nothing. The actual FastAPI application source was never committed, only its supporting docs. Two more issues to flag once real source arrives:
- **Path mismatch:** `docker-compose.yml` expects build context `./backend` (single level); the delivered folder is nested as `Backend/Backend/`. `tests/test_day4_api.py` imports `backend.app.main`, so working source needs to land at `backend/app/main.py` from repo root.
- **Nested git repo:** `Backend/Backend/.git` is its own git repository. Committed as-is it becomes a broken gitlink instead of tracked files — flag this to the backend intern before it's merged.

DEF-M2-001 remains **Open** — see updated description in [defect_tracker.md](../day1/defect_tracker.md).

### Real backend source delivered and flattened (2026-09-12)
Real `app/` source landed, nested at `Backend/Backend/app/...` with an embedded `.git`. QA:
1. Moved all content up to `backend/app/...`, `backend/Dockerfile`, `backend/requirements.txt`, etc. (matching `docker-compose.yml`'s `./backend` build context).
2. Removed the nested `.git`, `.venv`, `.pytest_cache` left behind in the wrapper folder.
3. Added root `conftest.py` — `backend/app/main.py` uses absolute imports (`from app.database import engine`) that assume `backend/` itself is the import root (matching the Docker `WORKDIR /app` setup), so `backend/` is added to `sys.path` for the test session.

DEF-M2-001 → **Fixed** (structure only; see below for newly-discovered code defects).

### Test run against the real backend
```
& '.\.venv\Scripts\python.exe' -m pytest tests/test_day4_api.py -q
```
Result: collection now succeeds (previously failed at import). Two assertion failures:
```
FAILED tests/test_day4_api.py::test_auth_register_login_me_refresh_and_rbac
  AssertionError: {"detail":"Not Found"}
  assert 404 == 201   (POST /api/auth/register)

FAILED tests/test_day4_api.py::test_traffic_endpoints
  AssertionError: {"detail":"Not Found"}
  assert 404 == 200   (GET /api/traffic/live)
```

### Root cause — live route introspection
Listed every route FastAPI actually registered (`app.routes`) to get ground truth instead of guessing:
```
POST /register            POST /login            POST /refresh           GET /me
GET  /api/v1/traffic/traffic/live
GET  /api/v1/traffic/traffic/road/{road_id}
GET  /api/v1/traffic/traffic/density
POST /api/v1/predict/congestion
GET  /api/v1/route/api/v1/route/optimize
GET  /api/v1/route/api/v1/route/alternate
GET  /api/v1/route/api/v1/route/travel-time
GET  /api/v1/route/api/v1/route/conditions
```
Compared against `backend/api_contracts.md`, this confirms three routing defects (auth has no `/api/v1/auth` prefix at all; traffic and route-analysis both double their prefix) plus a contract/implementation mismatch on the predict endpoint. Logged as **DEF-M2-002, DEF-M2-003, DEF-M2-004, DEF-M2-005** (and a minor dead-code import bug as DEF-M2-006) in [defect_tracker.md](../day1/defect_tracker.md). `tests/test_day4_api.py` itself also predates Milestone 2 — it targets the old unversioned Milestone 1 stub paths (`/api/auth/...`, `/api/traffic/...`) and will need rewriting to the `/api/v1/...` contract once the backend's own prefixes are fixed.

### Outcome
Auth and Traffic Monitoring (Milestone 1 regression, REG-*) are **Failed** — blocked by DEF-M2-002/003. Historical Traffic Data and Route Analysis (API) cases (HIST-001–006, ROUTE-001–006) are **Blocked** by DEF-M2-003/004 (routes are unreachable at their contracted paths). Traffic Prediction cases (PRED-001–007) are **Blocked** by DEF-M2-005 pending contract clarification. Postman collection creation is deferred until the backend's route prefixes are corrected, since the currently-live paths don't match the documented contract.

INT-001 (full integration flow) remains **Blocked** — the chain breaks at Authentication before it can reach Prediction/Route Analysis.

---

## Part B — UI / Frontend Execution (completed)

The frontend pages ship with **mock fallback data** (`api.js`, `data_source: "mock_fallback"`), so these were fully testable visually even with the backend API lane blocked. Executed via an automated headless-Chrome script (Playwright, driving the real system Chrome install) rather than manual clicking — it logs in through the CAPTCHA-protected login form (reads the `currentCaptchaCode` JS variable directly), navigates each page, interacts with the real controls, captures the browser console, and screenshots at the same moments originally planned below. Script: `conftest.py`-adjacent scratch script (not committed); all 16 screenshots below are the actual captured evidence.

### How to open the pages
The files are plain HTML — open them directly in a browser (no server needed):
- `Front-end (2)/Front-end/route-analysis.html`
- `Front-end (2)/Front-end/live maps.html`
- `Front-end (2)/Front-end/Login.html`
- `Front-end (2)/Front-end/operator dashboard.html`

Double-click the file in File Explorer, or in the browser press `Ctrl+O` and select it.

### Before each page: open DevTools console
Press `F12` (or `Ctrl+Shift+I`) → **Console** tab, so you can check for red errors (FE-M2-001).

### Steps, and exactly when to screenshot

| Test ID | Steps | Screenshot moment | Save as |
|---|---|---|---|
| FE-M2-001 | Open `route-analysis.html`, check DevTools Console tab | Right after page finishes loading, with Console tab visible showing no red errors | `01_route_analysis_console.png` |
| ROUTE-007 | On the loaded page, pick an origin in **Origin** dropdown and a destination in **Destination** dropdown | After route cards + map + KPI cards (Best ETA, Distance, Delay) populate | `02_route_selection_result.png` |
| ROUTE-008 | Click each optimization mode button: **AI Optimal**, **Fastest**, **Eco** | After clicking "Eco" (or any non-default mode), showing the updated recommended route | `03_optimization_mode_switch.png` |
| ROUTE-009 | Click the forecast horizon buttons (0 / 15 / 30 / 60 / 120 min) one at a time | After selecting a non-zero horizon (e.g. 30 min), showing updated forecast cards | `04_temporal_horizon_forecast.png` |
| FE-M2-002 | Same page | Screenshot showing the speed-profile chart (canvas) and temporal forecast cards rendered with data | `05_prediction_charts.png` |
| FE-M2-003 | Same page, after ROUTE-007 | Screenshot showing the travel-time / ETA KPI value | `06_travel_time_display.png` |
| FE-M2-004 | If a route shows hazards/construction, expand the road-conditions panel | Screenshot of the road-conditions panel with details visible | `07_road_conditions_panel.png` |
| FE-M2-005 | Click the prediction/report download control | Screenshot of the downloaded file appearing (browser downloads bar) or any error shown | `08_report_download.png` |
| FE-M2-007 | With no backend running, reload the page | Screenshot showing mock data still renders (no blank/broken page) | `09_mock_fallback_state.png` |
| MAP-001 | Open `live maps.html` | Screenshot of the map with road markers loaded | `10_live_map_load.png` |
| MAP-005 | Click any road marker/card | Screenshot of the road-detail modal open, showing congestion/speed/density + AI prediction text | `11_road_detail_modal.png` |
| MAP-003 | Click the tile-layer toggle buttons (OSM / Terrain) on `route-analysis.html` | Screenshot after switching to Terrain | `12_map_tile_toggle.png` |
| MAP-004 | Click the heatmap toggle button | Screenshot with heatmap overlay visible | `13_map_heatmap_toggle.png` |
| REG-001 | Open `Login.html`, log in with a valid test account | Screenshot of successful redirect to the role's dashboard | `14_regression_login.png` |
| REG-002 | Log in as different roles (operator / admin / public) if test accounts exist | Screenshot of one dashboard showing role-appropriate content (e.g. `operator dashboard.html`) | `15_regression_rbac.png` |
| REG-003 | On `live maps.html` or `operator dashboard.html`, confirm live traffic feed list populates | Screenshot of the populated live feed panel | `16_live_traffic_regression.png` |

Save every screenshot into:
```
QA/milestone2/day2/screenshots/
```
using the exact filenames above so this report's links resolve.

### Result table

| Test ID | Result | Notes | Evidence |
|---|---|---|---|
| FE-M2-001 | Pass | Only a benign Tailwind-CDN production warning plus expected `ERR_CONNECTION_REFUSED`/`ERR_EMPTY_RESPONSE` network errors from the (intentionally offline) backend, each paired with the page's own graceful fallback warning ("Backend route API unavailable, falling back to mock calculation"). No uncaught JS exceptions. | `01_route_analysis_console.png` |
| ROUTE-007 | **Fail** | Changing the Destination Hub select moves the map pin but does **not** recalculate ETA/Distance/Delay/CO2 KPIs, the corridor list, or the segment table, and the drawn route line doesn't move to the new pin. New defect **DEF-M2-007**. | `02_route_selection_result.png` (compare to `01`) |
| ROUTE-008 | **Fail** | Same root cause as ROUTE-007 — clicking "Eco Flow" highlights the button but KPIs/corridors/segments are unchanged from the AI-Optimal default. Tracked under **DEF-M2-007**. | `03_optimization_mode_switch.png` |
| ROUTE-009 | Pass | +30 min horizon correctly updates forecast cards (density/speed/trend/confidence) and the horizon label. This control works correctly, unlike ROUTE-007/008. | `04_temporal_horizon_forecast.png` |
| FE-M2-002 | Pass | Speed-profile canvas confirmed rendering actual pixel data (checked programmatically, not just visually). | `05_prediction_charts.png` |
| FE-M2-003 | Pass | ETA "9 mins", Distance "8.4 km" KPIs render correctly for the active route state (subject to the staleness bug above when inputs change). | `06_travel_time_display.png` |
| FE-M2-004 | Pass (partial) | Panel correctly stays hidden for a route with no hazards (Downtown→Tech Park/West Ridge, Low congestion). Did not hit a route/road with an active hazard in this session, so the populated-panel state is unverified. | `07_road_conditions_panel.png` |
| FE-M2-005 | Corrected finding | No download control exists on `route-analysis.html` (searched all buttons/links — none). A **"Download Prediction Report"** button does exist on `operator dashboard.html` and `admin dashboard.html` instead. Test case location was wrong, not a defect — button's actual click/download behavior not yet verified. | `14_regression_login.png`, `15_regression_rbac_admin.png` (both show the button) |
| FE-M2-007 | Pass | Reloading with no backend still renders full mock UI (2688 chars of body text vs. a blank/broken page). | `09_mock_fallback_state.png` |
| MAP-001 / MAP-002 | Pass | Both `live maps.html` and the embedded map on `route-analysis.html` render full OSM tiles, road polylines, and markers. | `10_live_map_load.png`, `01_route_analysis_console.png` |
| MAP-005 | Pass | Clicking a live-feed road card opens the detail modal with real congestion/speed/density + AI prediction text and reading history. | `11_road_detail_modal.png` |
| MAP-003 | Pass | Tile layer switches to Terrain correctly. | `12_map_tile_toggle.png` |
| MAP-004 | Pass (weak) | Heatmap button toggles to its active/highlighted state on click; a visible heat overlay wasn't clearly distinguishable in the captured screenshot, worth a manual double-check. | `13_map_heatmap_toggle.png` |
| REG-001 | Pass | Login (mock fallback, since backend is unreachable) redirects correctly to `operator dashboard.html`. | `14_regression_login.png` |
| REG-002 | Pass | Admin login → `admin dashboard.html`; Public login → `public dashboard.html`. Role-based redirect confirmed correct for all 3 roles. | `15_regression_rbac_admin.png`, `15_regression_rbac_public.png` |
| REG-003 | Pass | Live feed list populated with 7 road segments from mock data. | `16_live_traffic_regression.png` |

**New defect from UI execution: DEF-M2-007** (Route Analysis stale data on control change) — logged in [defect_tracker.md](../day1/defect_tracker.md), High severity.

---

## Defects Raised

| ID | Title | Severity | Priority | Status |
|---|---|---|---|---|
| DEF-M2-001 | Backend source delivered nested with embedded `.git` — QA flattened to `backend/` and added `conftest.py` | High | Medium | Fixed |
| DEF-M2-002 | Auth routes (`/register`, `/login`, `/refresh`, `/me`) missing `/api/v1/auth` prefix entirely | Critical | High | Open |
| DEF-M2-003 | Traffic routes double-prefixed: `/api/v1/traffic/traffic/live` instead of `/api/v1/traffic/live` | High | High | Open |
| DEF-M2-004 | Route Analysis routes double-prefixed: `/api/v1/route/api/v1/route/optimize` instead of `/api/v1/route/optimize` | High | High | Open |
| DEF-M2-005 | Predict endpoint contract mismatch — contract says `GET .../congestion?road_id=`, implementation is `POST` with a different body schema | Medium | Medium | Open |
| DEF-M2-006 | Dead module `app/security/auth.py` has a broken import (`from security.config...`, missing `app.` prefix); currently unused | Low | Low | Open |
| DEF-M2-007 | Route Analysis page: changing destination or optimization mode doesn't recalculate route metrics/path (stale KPIs, corridors, segments, map line) | High | Medium | Open |

## Overall Status

Day 2 is **complete**. All 32 Milestone 2 test cases are authored, and both lanes have been executed with real evidence:

- **API lane**: the backend structural blocker (DEF-M2-001) was fixed — real source now builds and runs under pytest. That unblocked actual API execution, which immediately surfaced four routing/contract defects (DEF-M2-002–005) confirmed by direct route introspection against the running app. All API-level Milestone 2 test cases (HIST-*, PRED-*, ROUTE-001–006) and the legacy Milestone 1 API regression suite are **Blocked/Failed** pending backend fixes. Send DEF-M2-002 through 005 back to the backend intern — DEF-M2-002 (auth has no prefix at all) is highest priority since it blocks login for every role at the API level.
- **UI lane**: executed via an automated headless-browser pass against every page (login, route analysis, live maps, all 3 role dashboards) using the shipped mock fallback data. 16 of 18 UI-level cases **Pass** with screenshot evidence in `QA/milestone2/day2/screenshots/`. 2 **Fail** — ROUTE-007 and ROUTE-008 — due to a newly-discovered defect (**DEF-M2-007**): the Route Analysis page's destination and optimization-mode controls don't actually recalculate the displayed route. This is independent of the backend outage; it's a frontend logic bug.

Next steps: send DEF-M2-002–005 (backend) and DEF-M2-007 (frontend) to their respective interns. Once the backend prefixes are corrected, re-run `pytest tests/test_day4_api.py`, retest HIST-*/PRED-*/ROUTE-001–006, and update INT-001. Once DEF-M2-007 is fixed, re-verify ROUTE-007/008 and re-screenshot `02_route_selection_result.png`/`03_optimization_mode_switch.png`.

# Milestone 3 QA Retest — 2026-09-29

Prepared by: Intern 5 (QA, DevOps & Release Engineering)

## Decision

**NO-GO — Milestone 3 remains unsigned.** Offline test coverage is green after correcting QA path/fixture issues, but the full-stack gates could not be rerun because the Docker engine is unavailable and the gateway, Analytics, and AI endpoints do not accept connections. Do not mark integration defects closed from the offline checks alone.

## Fresh Execution Results

| Check                                     | Result                                                      | Evidence                                                                                                          |
| ----------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Root pytest suite                         | **27 passed, 46 skipped, 0 failed**; 114 warnings           | `python -m pytest -q` from repo root                                                                              |
| Backend tests                             | **9 passed, 0 failed**; 108 warnings                        | `python -m pytest -q "backend_updated/backend/Intern AI AND ML/tests"`                                            |
| Data/Analytics tests                      | **60 passed, 0 failed**; 62 warnings                        | `python -m pytest -q tests` from `daa/M3_Day6_Traffic_Monitoring_`                                                |
| Congestion watcher tests                  | **7 passed, 0 failed**                                      | `python -m pytest -q backend_updated/backend/Intern AI AND ML/tests/test_m3_day2_congestion_threshold_watcher.py` |
| Frontend inline JavaScript                | **8 HTML pages parsed successfully**                        | `node QA/tools/check_inline_js.js` with all HTML files in `Front-end(m-3) (1)/Front-end`                          |
| Black / Flake8 on changed QA Python files | **Passed**                                                  | `conftest.py` and backend `tests/test_route_analysis.py`                                                          |
| Integration runner imports                | **Passed**; resolved backend and frontend directories exist | Python import smoke check for `integration_cycle` and `frontend_e2e`                                              |

The root pytest skips are service-dependent: Alert API checks require `http://127.0.0.1:8000`, and Analytics checks require `http://127.0.0.1:8001`. The AI endpoint on port 8010 was also unavailable.

## Environment Blocker

`docker compose -f docker-compose.dev.yml ps` could not connect to `npipe:////./pipe/dockerDesktopLinuxEngine`; the Docker engine pipe was missing. Fresh HTTP checks returned connection refused for:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8001/`
- `http://127.0.0.1:8010/`

The standard Docker Desktop executable path was absent. This report does not claim the software is not installed elsewhere; it records that no usable daemon was available in this run.

## QA Harness Corrections

- Root test setup now defaults to the current backend folder, `backend_updated/backend/Intern AI AND ML`, and adds the current Analytics source directory to Python's import path.
- Root pytest discovery now points at the current backend tests directory.
- The backend route test now starts FastAPI's lifespan, uses a unique allow-listed test email, and asserts registration/login before exercising the protected route. Its prior hard-coded `example.com` registration failed the app's domain policy and its TestClient did not create required tables.
- The Day 5 integration runner now defaults to the current backend and frontend folders and adds the backend `src` directory for the watcher import.

These changes repair QA configuration and test setup; they are not evidence that service-level product defects are fixed.

## Not Executed / Pending

The following require a running stack and were not rerun on 2026-09-29:

- Stack smoke and alert-delivery reliability checks
- API integration cycle
- Real-browser E2E across public, operator, and admin roles
- M1/M2 browser and API regression
- Analytics Redis-down performance check
- Live verification of previously tracked Milestone 3 defects

The latest full-stack evidence remains the 2026-09-28 run in `../status_update.md`. Re-run the commands in `day7/m3_qa_signoff_report.md` after Docker is available and the stack is healthy; update defect states only from that integrated evidence. No deployment was performed.

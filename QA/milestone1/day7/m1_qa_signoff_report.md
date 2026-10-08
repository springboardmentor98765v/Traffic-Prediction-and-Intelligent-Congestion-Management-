# Milestone 1 QA Sign-off Report

**Project:** TrafficVision AI, Smart Traffic Prediction & Congestion Management
**Prepared by:** Intern 5 (QA, DevOps & Release Engineering) · **Date:** 2026-10-02
**Build:** branch `Team-1` @ `ab2b15d` plus working tree · **Environment:** local `docker-compose.dev.yml`

## Verdict: CONDITIONAL SIGN-OFF ✅⚠️

The Milestone 1 increment works end to end on the local stack: register → login → role dashboard → live traffic → prediction, with RBAC enforced on role-gated routes. All High-priority functional paths pass.
Sign-off has three conditions, listed in section 5: one open High defect, and the CI workflow and quality gate are not live on GitHub yet.

## 1. Final validation cycle (Day 7)

| Cycle                      | Command / evidence                                                                               | Result                               |
| -------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------ |
| Smoke + integration (live) | `python QA/milestone1/day5/m1_live_stack_check.py` → `m1_final_smoke_output.txt`                 | **11/11 pass**                       |
| Automated M1 suite         | `pytest -v QA/milestone1/tests --junitxml` → `m1_final_pytest_output.txt`, `m1_pytest_junit.xml` | **76 pass, 5 xfail (known defects)** |
| RBAC (live, with operator) | Day 5 → `../day5/day5_live_stack_output.txt`                                                     | **13/13 pass**                       |
| UI (real browser, 3 roles) | Day 5 → `../day5/ui/`                                                                            | M1 checks all pass                   |
| Regression                 | Day 6 → `../day6/m1_day6_regression_report.md`                                                   | No regressions                       |

## 2. Acceptance criteria (SRS section 14)

| #   | Criterion                                                                          | Status | Evidence                                                                                                                             |
| --- | ---------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Project initialization, architecture and DB schema complete and documented         | ✅     | Backend `schema_design.md`, `jwt_approach.md`, `api_contracts.md`; traffic `database/schema.sql`                                     |
| 2   | Authentication and RBAC implemented and enforced on protected routes               | ⚠️     | Auth ✅ (TC-AUTH); RBAC ✅ on role-gated routes; monitoring and prediction are open to everyone (DEF-M1-003)                         |
| 3   | Live traffic monitoring and congestion tracking work and are exposed via REST      | ✅     | TC-TRF-01..09; 4,032 live DB rows served on the stack                                                                                |
| 4   | Frontend has a working login and a live dashboard driven by real backend data      | ✅     | Browser E2E; dashboard KPIs (179 vehicles, 8.24 veh/km) = `/traffic/density`                                                         |
| 5   | AI Engine heuristic stub reachable end to end and shown on the dashboard           | ✅*    | Stub `heuristic-v0` on :8010 ✅; the gateway and dashboard now show the M2 `model-v1`, the planned successor                         |
| 6   | All services run together and pass integration/smoke tests in local Docker Compose | ✅     | 13/13 live checks; postgres, redis, backend and ai healthy                                                                           |
| 7   | CI enforces lint, build and test on every PR                                       | ❌     | Workflow written but **not committed** (`.github/` untracked); code-quality job would fail (DEF-M1-007); one test fails (DEF-M1-006) |
| 8   | Every tool used was free / open-source                                             | ✅     | pytest, pytest-cov, Playwright, Flake8, Black, ESLint, Prettier, Docker, GitHub Actions free tier                                    |
| 9   | No production deployment activity                                                  | ✅     | No deploy job in `ci.yml`; no cloud config; all testing local                                                                        |

\* Criterion 5 was met in Milestone 1 and has since been superseded as planned. The M2 model sits on the same contract (`road_id, predicted_level, confidence`), and the stub is still served for reference.

## 3. Defect status

| Severity | Open | Closed | IDs (open)                                  |
| -------- | ---: | -----: | ------------------------------------------- |
| Critical |    0 |      0 |                                             |
| High     |    1 |      2 | DEF-M1-001                                  |
| Medium   |    3 |      0 | DEF-M1-003, DEF-M1-006, DEF-M1-007          |
| Low      |    3 |      0 | DEF-M1-002, DEF-M1-004, DEF-M1-008          |
| Accepted |    1 |        | DEF-M1-009 (static HTML instead of Next.js) |

Closed: DEF-001 (legacy Day 4 test conflict) and DEF-M1-005 (stale AI container). Full list: `../day1/defect_tracker.md`.

## 4. Deviations from the SRS (for the mentor)

| SRS says                      | Repo has                                      | QA view                                                            |
| ----------------------------- | --------------------------------------------- | ------------------------------------------------------------------ |
| Next.js + Tailwind frontend   | Static HTML + Tailwind + `api.js`             | Functionally meets FR-07/08; accepted as DEF-M1-009                |
| PostgreSQL                    | TimescaleDB (PostgreSQL 16 + extension)       | Superset, OK                                                       |
| `/auth/register` takes `role` | Role ignored; public sign-up is always PUBLIC | Security improvement; privileged roles are provisioned by an admin |
| `/auth/me` returns `name`     | Returns `username`                            | DEF-M1-002                                                         |

## 5. Conditions to close sign-off

| #   | Condition                                                                                      | Owner    |
| --- | ---------------------------------------------------------------------------------------------- | -------- |
| 1   | Fix DEF-M1-001: add `min_length` validation on name and password in `UserCreate`               | Intern 1 |
| 2   | Commit `.github/` (workflow and defect template) and open a PR so CI runs on GitHub (FR-10)    | Intern 5 |
| 3   | Make CI green: fix DEF-M1-006 (alert-key test) and DEF-M1-007 (format and lint pass per owner) | All      |

DEF-M1-003 (public monitoring routes) needs a mentor decision: document the routes as public on purpose, or require a token.

## 6. No-deployment confirmation

I confirm that no deployment, production packaging or cloud release activity was performed in Milestone 1. All testing used in-process TestClient runs or the local Docker Compose stack. Deployment remains scheduled for after Milestone 4.

**Intern 5, QA, DevOps & Release Engineering · 2026-10-02**

# Milestone 1 Test Plan — TrafficVision AI

**Owner:** Intern 5 (QA, DevOps & Release Engineering)
**Source of requirements:** `Milestone1_SRS_TrafficVisionAI(1).pdf` (sections 5–7, 12–14)
**Supersedes:** `docs/TEST-PLAN-MILESTONE-1.md`. The old plan assumed a deployed test environment and release-candidate approval, and it covered alerts and routes. None of that is in Milestone 1 scope.

## 1. Objective

Confirm that the Milestone 1 build works end to end inside the local `docker-compose.dev.yml` stack:

- Authentication and RBAC (Admin / Traffic Operator / Public)
- The live Traffic Monitoring pipeline and its APIs
- The AI Engine heuristic prediction stub
- The login page and live dashboard that consume those APIs

All of this is checked against the API contracts frozen on Day 2 (SRS section 7).

**No deployment.** Every test runs locally, either in-process or against the local compose stack. Production deployment is out of scope until after Milestone 4.

## 2. Requirements under test

| Req   | Requirement                                           | Owner    | Covered by                      |
| ----- | ----------------------------------------------------- | -------- | ------------------------------- |
| FR-01 | Register / login, JWT carries the role                | Intern 1 | TC-AUTH-01..21                  |
| FR-02 | Protected endpoints enforce RBAC                      | Intern 1 | TC-RBAC-01..10                  |
| FR-03 | Simulated real-time traffic ingested per road segment | Intern 2 | TC-TRF-01..04, live smoke       |
| FR-04 | Congestion level computed per road segment            | Intern 2 | TC-TRF-03, TC-TRF-06, TC-TRF-09 |
| FR-05 | Live traffic / congestion exposed via REST            | Intern 2 | TC-TRF-01..08                   |
| FR-06 | Heuristic congestion-prediction endpoint              | Intern 3 | TC-PRED-01..08                  |
| FR-07 | Web login reaches a role-aware dashboard              | Intern 4 | TC-UI-01..06, browser E2E       |
| FR-08 | Dashboard shows live traffic and the prediction       | Intern 4 | Browser E2E (Day 5)             |
| FR-09 | All services run together in local Docker Compose     | Intern 5 | Day 2 config check, Day 5 smoke |
| FR-10 | PRs pass lint / build / test before merge             | Intern 5 | Day 2 CI review, Day 6 report   |
| FR-11 | Documented integration and RBAC test cycle            | Intern 5 | Day 5 and Day 7 reports         |

## 3. Test levels and tools (all free / open-source)

| Level                 | What                                                                                               | Tool                                                |
| --------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Unit                  | Congestion rule, heuristic thresholds                                                              | pytest                                              |
| API / contract        | Every frozen route: status codes, response fields, error paths                                     | pytest + FastAPI TestClient (`QA/milestone1/tests`) |
| RBAC                  | Role claims, 401/403 on role-gated routes, forged/expired tokens                                   | pytest                                              |
| Integration (live)    | Register → login → traffic → prediction → RBAC through the gateway on :8000 and AI Engine on :8010 | `day5/m1_live_stack_check.py` (requests)            |
| UI end-to-end         | Real browser login per role → correct dashboard → live data on screen                              | Playwright (`QA/milestone3/day5/frontend_e2e.py`)   |
| Static / code quality | flake8, black, ESLint, Prettier, inline-script parse                                               | CI `code-quality` job                               |

## 4. Environment

- `docker-compose.dev.yml`: postgres (TimescaleDB pg16), redis, backend gateway :8000, ai :8010, analytics :8001 (analytics is Milestone 3 and not tested here).
- In-process suite: the root `conftest.py` points `DATABASE_URL` at a throwaway SQLite file, so the suite runs in CI without Docker.
- Test accounts: Public users self-register. Admin and Operator users are provisioned directly in the `users` table, because public sign-up cannot create privileged roles. This is by design.

## 5. Entry criteria

- API contracts frozen (Day 2 checkpoint, SRS 12.2).
- `docker-compose.dev.yml` brings up postgres, redis and the backend services healthy.
- CI runs on every PR to `main` / `develop`.

## 6. Exit criteria (Milestone 1 sign-off)

- All High-priority test cases pass. A known defect is allowed only if it is logged and has an owner.
- No open Critical defects. Open High defects need a documented owner and target.
- The full integration cycle passes inside the local compose stack.
- Regression and code-quality reports are published (Day 6).
- No deployment activity has been performed.

## 7. Defect management

Defects are logged in `day1/defect_tracker.md` and on GitHub Issues using `.github/ISSUE_TEMPLATE/defect-template.md`. Severity and SLA follow `docs/BUG-TRACKING-BOARD.md`. Every open defect that has an automated reproduction is pinned by a `strict` xfail test. When the fix lands, that test starts passing unexpectedly, which forces the marker to be removed.

## 8. Schedule (SRS section 9)

| Day | QA activity                                                                 | Output            |
| --- | --------------------------------------------------------------------------- | ----------------- |
| 1   | Lint/format tooling, PR checklist, branch policy, test plan, defect tracker | `day1/`           |
| 2   | CI (lint + build + test, no deploy), `docker-compose.dev.yml`               | `day2/`           |
| 3   | Test cases for Auth/RBAC, Monitoring, Prediction; automated suite skeleton  | `day3/`, `tests/` |
| 4   | Execute Auth + Monitoring tests, log defects, CI runs tests                 | `day4/`           |
| 5   | Full integration cycle in compose, RBAC end-to-end                          | `day5/`           |
| 6   | Regression after fixes, coverage check, static code-quality report          | `day6/`           |
| 7   | Final validation, QA sign-off, test summary                                 | `day7/`           |

## 9. Risks

| Risk                                           | Mitigation                                                                   |
| ---------------------------------------------- | ---------------------------------------------------------------------------- |
| Contract drift after Day 2                     | Contract tests assert every frozen route is in OpenAPI (TC-GW-02)            |
| Running containers older than the compose file | Day 5 checks container env against the compose file; recreate before testing |
| Stub replaced by the M2 model                  | Stub tested directly on the AI Engine; gateway route tested separately       |
| Privileged test accounts cannot self-register  | Provision Admin/Operator in the DB (fixtures and documented SQL)             |

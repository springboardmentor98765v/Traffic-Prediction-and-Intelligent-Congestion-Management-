# Milestone 1 Defect Tracker

Severity, priority and SLA follow `docs/BUG-TRACKING-BOARD.md`. Use `.github/ISSUE_TEMPLATE/defect-template.md` to open the GitHub issue.
**Pinned** means a `strict` xfail test reproduces the defect. Once it's fixed, that test reports XPASS and fails the run until the marker is removed.

Last updated: 2026-10-02 (Day 7 final cycle)

| ID         | Title                                                                                                           | Area / Owner         | Severity | Priority | Status   | Found | Pinned by                                |
| ---------- | --------------------------------------------------------------------------------------------------------------- | -------------------- | -------- | -------- | -------- | ----- | ---------------------------------------- |
| DEF-001    | Seeded admin account conflicts with the registration flow in the Day 4 RBAC test (legacy)                       | QA suite / Intern 5  | High     | High     | Closed   | Day 4 | `tests/test_day4_api.py` now passes      |
| DEF-M1-001 | `/auth/register` accepts an empty password and an empty name (201)                                              | Auth / Intern 1      | High     | High     | Open     | Day 4 | TC-AUTH-05, TC-AUTH-06                   |
| DEF-M1-002 | `/auth/me` returns `username`; frozen contract says `name`                                                      | Auth / Intern 1      | Low      | Medium   | Open     | Day 4 | TC-AUTH-17                               |
| DEF-M1-003 | M1 traffic and prediction routes require no token                                                               | Gateway / Intern 1   | Medium   | Medium   | Open     | Day 4 | TC-RBAC-10                               |
| DEF-M1-004 | Login `role` format is inconsistent: `PUBLIC` vs lower-case `admin` / `operator`                                | Auth / Intern 1      | Low      | Low      | Open     | Day 4 | TC-RBAC-09                               |
| DEF-M1-005 | Running `ai` container was older than `docker-compose.dev.yml`, so the stub returned 503                        | Local env / Intern 5 | High     | High     | Closed   | Day 5 | `day5/m1_live_stack_check.py`            |
| DEF-M1-006 | `test_tc_al_31` (M3 suite) fails locally: test reads the key from `.env.dev`, backend uses the conftest default | QA suite / Intern 5  | Medium   | Medium   | Open     | Day 6 | `QA/milestone3/tests/test_alerts_api.py` |
| DEF-M1-007 | CI `code-quality` job is red: flake8 / black / ESLint / Prettier findings in service code                       | All services         | Medium   | Medium   | Open     | Day 6 | `day6/day6_code_quality_output.txt`      |
| DEF-M1-008 | Frontend silently swaps in a client-side prediction when the predict call fails                                 | Frontend / Intern 4  | Low      | Low      | Open     | Day 5 | Manual (api.js `predictAPI` catch block) |
| DEF-M1-009 | Frontend is static HTML/JS, not Next.js + Tailwind as the SRS tech stack says                                   | Frontend / Intern 4  | Low      | Low      | Accepted | Day 1 | Spec deviation, see sign-off report      |

## Details

### DEF-M1-001: Registration accepts empty credentials

- **Steps:** `POST /api/v1/auth/register` with `{"name": "", "email": "<new>@gmail.com", "password": ""}`
- **Expected:** 422 validation error.
- **Actual:** 201, and the account is created. Reproduced in-process and on the live stack (`curl` → 201, 2026-10-02).
- **Cause:** `UserCreate` in `app/schemas/user.py` has no `min_length` on `name` or `password`.
- **Suggested fix:** `name: constr(min_length=1)`, plus a minimum password length (for example 8).

### DEF-M1-002: `/auth/me` field name differs from the contract

- **Contract (SRS 7.1):** `200 { user_id, name, role }`
- **Actual:** `{ user_id, username, role }`. The frontend copes because it reads `data.username || data.name`.

### DEF-M1-003: Monitoring and prediction routes are unauthenticated

- `GET /api/v1/traffic/*` and `GET /api/v1/predict/congestion` return 200 without a token.
- Only the alert routes check roles. FR-02 says protected endpoints enforce RBAC. Public read access may be intended (the Public/Commuter role exists), but it is not documented in the contract.
- **Action:** Intern 1 either documents these routes as public or adds `Depends(get_current_user)`.

### DEF-M1-004: Login role casing

- Login returns `"PUBLIC"` for users but `"admin"` / `"operator"` for staff, while `/auth/me` returns upper case for all roles. The frontend upper-cases it, so there is no visible impact.

### DEF-M1-005: Stale AI container (closed)

- `trafficvision-ai-dev` had been created on 2026-09-28. `TRAFFIC_API_URL: http://backend:8000/...` was added to the compose file on 2026-09-30. Without it, the stub called `127.0.0.1:8000` (itself) and returned 503.
- **Fix:** `docker compose -f docker-compose.dev.yml up -d --no-deps ai`. The re-run passed.
- **Prevention:** run `docker compose up -d` (not just `start`) after pulling compose changes.

### DEF-M1-006: M3 alert-key test is environment-dependent

- The test builds its service-key header from `.env.dev`, but the in-process backend reads `ALERT_SERVICE_KEY`, which the root `conftest.py` defaults to a test key, so the service returns 403. It fails in isolation too, so it is not caused by the M1 suite.

### DEF-M1-007: Code-quality gate red

- See `day6/m1_day6_code_quality_report.md`. The real-bug findings are 6 bare `except:` in `app/services/traffic_service.py`, an F811 redefinition of `get_road_condition`, and 6 `no-useless-catch` / 4 `no-empty` ESLint errors.

### DEF-M1-008: Silent prediction fallback

- `api.js` falls back to a density-threshold guess with a hard-coded confidence when `/predict/congestion` fails, without showing the user. This can hide a prediction-service outage on the dashboard.

# Day 6: Regression Report

**Executed:** 2026-10-02 · **Build:** `Team-1` @ `ab2b15d` plus working tree
**Evidence:** `day6_regression_output.txt`, `day6_coverage_output.txt`

## 1. Regression run (everything CI runs)

| Suite                                                                                      | Result                                                            |
| ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Root `pytest -q`: `tests/`, backend `tests/`, `QA/milestone1/tests`, `QA/milestone3/tests` | **138 passed, 1 failed, 21 skipped, 5 xfailed**                   |
| Analytics service (Intern 2), `daa/M3_Day6_Traffic_Monitoring_/tests`                      | **60 passed**                                                     |
| AI Engine (Intern 3), `ai-engine/tests`                                                    | **19 passed**                                                     |
| Milestone 1 live stack check (`day5/m1_live_stack_check.py`)                               | **11/11** without operator credentials (13/13 with them on Day 5) |

- **21 skipped:** M3 tests that need the analytics service on :8001, which is down. They are outside M1 scope.
- **5 xfailed:** M1 defects DEF-M1-001 to 004, pinned on purpose.
- **1 failed:** `QA/milestone3/tests/test_alerts_api.py::test_tc_al_31_producer_service_key_is_accepted` returns 403 instead of 201. It also fails when run alone, so the M1 suite didn't cause it. The test reads its service key from `.env.dev`, while the in-process backend uses the default from the root `conftest.py`. Logged as **DEF-M1-006** (QA harness, Medium). It will turn the CI `tests` job red until fixed.

### Re-test of earlier defects

| Defect     | Re-test                                                                         | Status |
| ---------- | ------------------------------------------------------------------------------- | ------ |
| DEF-001    | `tests/test_day4_api.py` passes 5/5                                             | Closed |
| DEF-M1-005 | Recreated `ai` container has `TRAFFIC_API_URL`; stub returns 200                | Closed |
| DEF-M1-001 | TC-AUTH-05/06 still xfail; live `curl` with an empty password still returns 201 | Open   |
| DEF-M1-002 | TC-AUTH-17 still xfail                                                          | Open   |
| DEF-M1-003 | TC-RBAC-10 still xfail                                                          | Open   |
| DEF-M1-004 | TC-RBAC-09 still xfail                                                          | Open   |

No regressions: every test that passed on Days 4 and 5 still passes.

## 2. Automated test coverage (M1 suite, `pytest --cov`)

| Module                              | Statements | Coverage | Comment                                                                                                                             |
| ----------------------------------- | ---------: | -------: | ----------------------------------------------------------------------------------------------------------------------------------- |
| `app/main.py` (gateway)             |         21 | **100%** |                                                                                                                                     |
| `app/routes/auth.py`                |         96 |  **96%** | Uncovered: duplicate-username 400 (line 50), expired refresh token (132), two `user_id is None` guards (121, 152)                   |
| `app/schemas/user.py`               |         32 |  **91%** | Gmail-typo and the 72-byte password branch                                                                                          |
| `app/security/password.py`          |          8 | **100%** |                                                                                                                                     |
| `app/routes/traffic.py`             |         51 |      55% | Uncovered lines are M2 routes (`/history`, `/aggregate`, `/metrics/*`)                                                              |
| `app/routes/predict.py`             |         95 |      56% | Uncovered lines are M2 routes (peak hours, delay, legacy POST)                                                                      |
| `app/services/traffic_service.py`   |        208 |      27% | The Postgres branch is not reached in-process (SQLite sample fallback). It is covered by the live stack check against 4,032 DB rows |
| `ai-engine/app.py`                  |         87 |      62% | The M1 stub is fully covered; the rest is M3 anomalies and recommendations                                                          |
| **Total (backend app + ai-engine)** |   **1152** |  **45%** | M1 code paths are close to fully covered; the gaps are M2/M3 routes                                                                 |

Coverage was measured with `pytest-cov` (free), installed into the local `.venv` for this run. It is not yet in any `requirements.txt`; add it to CI if a coverage gate is wanted in M2.

## 3. Go / no-go for Day 7

**Go**, with conditions:

- No M1 regressions, and every High-priority functional path passes.
- One High defect is still open (DEF-M1-001, empty credentials). It needs an owner and a target before sign-off (see Day 7).
- The CI jobs will be red on GitHub until DEF-M1-006 and DEF-M1-007 are fixed (see the code-quality report).

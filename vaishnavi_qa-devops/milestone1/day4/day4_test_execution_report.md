# Day 4: Functional Test Execution (Auth and Traffic Monitoring)

**Executed:** 2026-10-02 · **Build:** branch `Team-1` @ `ab2b15d` plus working tree · **Runner:** pytest, in-process gateway (FastAPI TestClient)
**Command:** `python -m pytest -v -rxX QA/milestone1/tests/test_m1_auth.py QA/milestone1/tests/test_m1_traffic.py`
**Evidence:** `day4_pytest_output.txt`

## Summary

| Area                        |  Cases | Passed | Failed (known defect) |
| --------------------------- | -----: | -----: | --------------------: |
| Authentication (TC-AUTH)    |     21 |     18 |                     3 |
| Traffic Monitoring (TC-TRF) |      9 |      9 |                     0 |
| **Total**                   | **30** | **27** |                 **3** |

The 3 failures are `strict` xfail tests. Each one reproduces a logged defect, so the run is green while the defect stays visible.

## Results by endpoint

| Endpoint                 | Result | Notes                                                                                                                    |
| ------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------ |
| `POST /auth/register`    | ⚠️     | Valid, duplicate (409), bad-domain and bad-format cases pass. **Empty password / empty name are accepted** (DEF-M1-001)  |
| `POST /auth/login`       | ✅     | Tokens and role returned; 401 for a wrong password or unknown email; same error text for both                            |
| `POST /auth/refresh`     | ✅     | Issues a working access token; rejects access tokens and garbage                                                         |
| `GET /auth/me`           | ⚠️     | Rejects missing, expired, malformed and refresh tokens. Returns `username` instead of the contract's `name` (DEF-M1-002) |
| `GET /traffic/live`      | ✅     | All contract fields present; valid levels; unique road IDs                                                               |
| `GET /traffic/road/{id}` | ✅     | Contract fields and history; 404 for an unknown road; matches the live feed                                              |
| `GET /traffic/density`   | ✅     | `total_roads` matches the live feed; average density within min..max                                                     |
| Congestion rule          | ✅     | All four bands and the capacity-0 guard                                                                                  |

## Defects raised today

| ID         | Title                                                | Sev  | Pri    | Owner    |
| ---------- | ---------------------------------------------------- | ---- | ------ | -------- |
| DEF-M1-001 | Register accepts an empty password and an empty name | High | High   | Intern 1 |
| DEF-M1-002 | `/auth/me` returns `username`, contract says `name`  | Low  | Medium | Intern 1 |
| DEF-M1-003 | Monitoring and prediction routes need no token       | Med  | Medium | Intern 1 |
| DEF-M1-004 | Login role casing is inconsistent across roles       | Low  | Low    | Intern 1 |

Full details are in `../day1/defect_tracker.md`.

## Earlier Day 4 report (`QA/Day4-Test-Execution-Report.md`)

That report recorded **DEF-001** ("User already exists": seeded admin conflicting with registration) and 1 of 2 tests passing. The test was later rewritten to use unique e-mail addresses (DEF-M3-001), and `tests/test_day4_api.py` now passes **5/5**. **DEF-001 is closed.**

## CI now runs the tests

`QA/milestone1/tests` was added to `testpaths` in `pyproject.toml`. The `pytest -q` step in the CI `tests` job therefore runs this suite on every PR, together with the existing backend and M3 suites.

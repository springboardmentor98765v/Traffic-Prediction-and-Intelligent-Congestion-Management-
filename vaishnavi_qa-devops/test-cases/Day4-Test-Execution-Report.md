# Day 4 Test Execution Report

## Scope

- Auth API functional tests:
  - Register
  - Login
  - Refresh token
  - /me
  - RBAC
- Traffic Monitoring API tests:
  - /traffic/live
  - /traffic/road/{road_id}
  - /traffic/density

## Test Execution Summary

| Category               | Test Count | Passed | Failed |
| ---------------------- | ---------: | -----: | -----: |
| Authentication API     |          1 |      0 |      1 |
| Traffic Monitoring API |          1 |      1 |      0 |
| Total                  |          2 |      1 |      1 |

## Results

### AUTH-API-001: Register/Login/Refresh/Me/RBAC

- Status: Failed
- Expected result: Successful registration for a new user and admin, token generation, profile retrieval, refresh, and RBAC denial for non-admin access.
- Actual result: Registration fails for the predefined admin account because it already exists in the seeded in-memory datastore. The test stops before the RBAC assertion can evaluate properly.
- Evidence:
  - Command run: `& '.\.venv\Scripts\python.exe' -m pytest tests/test_day4_api.py -q`
  - Result: `1 failed, 1 passed in 1.94s`
  - Failure excerpt: `AssertionError: {"detail":"User already exists"}`

### TRAFFIC-API-001: Traffic endpoints

- Status: Passed
- Expected result: `/api/traffic/live` returns a list, `/api/traffic/road/RD-101` returns the road payload, and `/api/traffic/density` returns an average plus road list.
- Actual result: All traffic endpoint assertions passed.
- Evidence:
  - Command run: `& '.\.venv\Scripts\python.exe' -m pytest tests/test_day4_api.py -q`
  - Result: `1 passed` for the traffic test block.

## Defects Raised

| ID      | Title                                                                        | Severity | Priority | Status |
| ------- | ---------------------------------------------------------------------------- | -------- | -------- | ------ |
| DEF-001 | Seeded admin account conflicts with registration flow during RBAC validation | High     | High     | Open   |

## Defect Details

### DEF-001

- Bug description: The in-memory user store seeds an admin account with the same email used in the RBAC test, causing user registration to fail with 409 Conflict before role checks can be validated.
- Severity: High
- Priority: High
- Steps to reproduce:
  1. Start the FastAPI backend.
  2. Send POST `/api/auth/register` with email `admin@example.com` and role `admin`.
  3. Observe 409 Conflict due to existing user.
- Evidence: Test output from the failing pytest execution.

## CI Status

- CI workflow has been extended in [.github/workflows/ci.yml](.github/workflows/ci.yml) to run `pytest -q` on every pull request.
- Local execution evidence: pytest was run successfully in the project virtual environment.
- GitHub-hosted PR status could not be confirmed from this environment because there is no active GitHub repository push/remote validation or issue tracker connected here.

## Overall Status

The Day 4 task is partially complete: the CI pipeline has been updated, the required traffic endpoint checks pass, and the failure has been documented. The remaining blocker is the RBAC/auth registration logic and the lack of a connected GitHub issue tracker for real issue posting.

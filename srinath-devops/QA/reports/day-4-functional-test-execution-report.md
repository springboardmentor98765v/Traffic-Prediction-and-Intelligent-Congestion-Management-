# Day 4 — Functional Test Execution Report

## Project
TrafficVision AI — Milestone 1

## Role
Intern 5 — DevOps

## Objective
Execute functional validation for Authentication and Traffic Monitoring APIs as the live services become available, record confirmed defects with severity and priority, and ensure CI runs automated API tests on Pull Requests.

## Authentication Functional Tests

| Test ID | Test Scenario | Expected Result | Actual Result | Status | Defect ID |
|---|---|---|---|---|---|
| AUTH-001 | Register with valid details | User registered and user ID returned | Live API required | Pending | — |
| AUTH-002 | Login with valid credentials | Access token, refresh token and role returned | Live API required | Pending | — |
| AUTH-003 | Login with invalid credentials | Login rejected | Live API required | Pending | — |
| AUTH-004 | Refresh using valid refresh token | New access token returned | Live API required | Pending | — |
| AUTH-005 | Get current user with valid token | User information returned | Live API required | Pending | — |
| AUTH-006 | Access protected resource without token | Access denied | Live API required | Pending | — |
| AUTH-007 | Access protected resource with invalid token | Access denied | Live API required | Pending | — |

## Traffic Monitoring Functional Tests

| Test ID | Test Scenario | Expected Result | Actual Result | Status | Defect ID |
|---|---|---|---|---|---|
| TRAF-001 | Request live traffic | Live traffic records returned | Live API required | Pending | — |
| TRAF-002 | Request valid road ID | Correct road-specific traffic returned | Live API required | Pending | — |
| TRAF-003 | Request invalid road ID | Appropriate error returned | Live API required | Pending | — |
| TRAF-004 | Request density metrics | Density metrics returned | Live API required | Pending | — |
| TRAF-005 | Verify density calculation | Follows implemented calculation rule | Live API required | Pending | — |
| TRAF-006 | Verify congestion logic | Follows implemented rule | Live API required | Pending | — |
| TRAF-007 | Verify live response fields | Required traffic fields present | Live API required | Pending | — |

## CI Test Execution on Pull Requests

```text
Pull Request
     ↓
GitHub Actions
     ↓
Lint → Build → Automated API Tests
     ↓
PASS / FAIL
```

### DevOps Verification Status

- [x] CI workflow includes automated API test execution.
- [x] API tests are configured to run with `pytest -q`.
- [x] CI is configured for Pull Requests.
- [x] A failing pytest command will fail the CI job.
- [x] No deployment stage is included.
- [ ] Live Authentication API execution verified.
- [ ] Live Traffic Monitoring API execution verified.
- [ ] CI API tests verified against live backend service.

## Defect Handling

No application defect is recorded without an actual observed failure. The current API execution blocker is treated as an environment/integration dependency until the live services are available.

## Execution Summary

| Area | Planned | Executed | Passed | Failed | Pending |
|---|---:|---:|---:|---:|---:|
| Authentication | 7 | 0 | 0 | 0 | 7 |
| Traffic Monitoring | 7 | 0 | 0 | 0 | 7 |
| CI automated tests | 1 | 0 | 0 | 0 | 1 |

## Current Status

**CI CONFIGURED / FUNCTIONAL API VALIDATION PENDING LIVE SERVICES**

The remaining functional execution depends on the availability of the Authentication and Traffic Monitoring APIs. No unverified Pass/Fail results have been added.

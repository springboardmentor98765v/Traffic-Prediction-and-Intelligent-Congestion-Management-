# Milestone 1 Test Cases

Automated in `QA/milestone1/tests/` (test function names start with the lower-case ID, for example `test_tc_auth_01_...`).
Replaces the earlier drafts `QA/auth_test_cases.md` and `QA/traffic_monitoring_test_cases.md`. Those drafts had 8 cases each, used "location" instead of `road_id`, and had no coverage for refresh, `/me`, `/density`, prediction or role checks.

Priority: H = High, M = Medium, L = Low. Result is from the Day 7 final run (2026-10-02).

## Authentication (SRS 7.1, FR-01): `test_m1_auth.py`

| ID         | Test case                                                | Expected                                                                                   | Pri | Result          |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --- | --------------- |
| TC-AUTH-01 | Register a valid new user                                | 201 with `user_id`                                                                         | H   | Pass            |
| TC-AUTH-02 | Register an existing email                               | 409                                                                                        | H   | Pass            |
| TC-AUTH-03 | Register with a non-allow-listed domain                  | 422                                                                                        | M   | Pass            |
| TC-AUTH-04 | Register with a malformed email                          | 422                                                                                        | M   | Pass            |
| TC-AUTH-05 | Register with an empty password                          | 422                                                                                        | H   | Fail DEF-M1-001 |
| TC-AUTH-06 | Register with an empty name                              | 422                                                                                        | M   | Fail DEF-M1-001 |
| TC-AUTH-07 | Login with valid credentials                             | 200, `access_token`, `refresh_token`, `role`; JWT has a role claim and `token_type=access` | H   | Pass            |
| TC-AUTH-08 | Login with the wrong password                            | 401                                                                                        | H   | Pass            |
| TC-AUTH-09 | Login with an unknown email                              | 401                                                                                        | H   | Pass            |
| TC-AUTH-10 | Login with an empty body                                 | 422                                                                                        | M   | Pass            |
| TC-AUTH-11 | Login error message doesn't reveal which field was wrong | Same `detail` for wrong email and wrong password                                           | M   | Pass            |
| TC-AUTH-12 | `/me` with a valid token                                 | 200, `user_id`, `role=PUBLIC`                                                              | H   | Pass            |
| TC-AUTH-13 | `/me` without a token                                    | 401/403                                                                                    | H   | Pass            |
| TC-AUTH-14 | `/me` with a malformed token                             | 401                                                                                        | H   | Pass            |
| TC-AUTH-15 | `/me` with an expired token                              | 401                                                                                        | H   | Pass            |
| TC-AUTH-16 | `/me` with a refresh token instead of an access token    | 401                                                                                        | H   | Pass            |
| TC-AUTH-17 | `/me` returns the contract fields `user_id, name, role`  | All three present                                                                          | L   | Fail DEF-M1-002 |
| TC-AUTH-18 | Refresh with a valid refresh token                       | 200 and a new token that works on `/me`                                                    | H   | Pass            |
| TC-AUTH-19 | Refresh with an access token                             | 401                                                                                        | H   | Pass            |
| TC-AUTH-20 | Refresh with a garbage token                             | 401                                                                                        | M   | Pass            |
| TC-AUTH-21 | Password not stored in plain text                        | Stored hash ≠ password                                                                     | H   | Pass            |

## RBAC (FR-02): `test_m1_rbac.py`

| ID         | Test case                                                        | Expected                                                | Pri | Result          |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------------- | --- | --------------- |
| TC-RBAC-01 | Self-registration asking for `role=admin`                        | Account created as PUBLIC                               | H   | Pass            |
| TC-RBAC-02 | JWT claim and `/me` role for Public / Operator / Admin (3 cases) | `user`/`PUBLIC`, `operator`/`OPERATOR`, `admin`/`ADMIN` | H   | Pass            |
| TC-RBAC-03 | Public creates an alert (role-gated)                             | 403                                                     | H   | Pass            |
| TC-RBAC-04 | Anonymous user creates an alert                                  | 401/403                                                 | H   | Pass            |
| TC-RBAC-05 | Operator and Admin create an alert (2 cases)                     | 201                                                     | H   | Pass            |
| TC-RBAC-06 | Public marks an alert as read                                    | 403                                                     | H   | Pass            |
| TC-RBAC-07 | Operator marks an alert as read                                  | 200                                                     | H   | Pass            |
| TC-RBAC-08 | Admin token signed with the wrong key                            | 401/403 on alerts and `/me`                             | H   | Pass            |
| TC-RBAC-09 | Login `role` format is consistent across roles                   | Same casing for all roles                               | L   | Fail DEF-M1-004 |
| TC-RBAC-10 | Monitoring routes require authentication                         | 401/403 without a token                                 | M   | Fail DEF-M1-003 |

## Traffic Monitoring (SRS 7.2, FR-03..05): `test_m1_traffic.py`

| ID        | Test case                             | Expected                                                           | Pri | Result |
| --------- | ------------------------------------- | ------------------------------------------------------------------ | --- | ------ |
| TC-TRF-01 | `GET /traffic/live`                   | 200, non-empty list                                                | H   | Pass   |
| TC-TRF-02 | Live item fields                      | `road_id, vehicle_count, density, congestion_level, updated_at`    | H   | Pass   |
| TC-TRF-03 | Live values are valid                 | Counts and density ≥ 0, level in {Low, Medium, High, Severe}       | H   | Pass   |
| TC-TRF-04 | Road IDs are unique in the live feed  | No duplicates                                                      | M   | Pass   |
| TC-TRF-05 | `GET /traffic/road/{id}`              | 200, `road_id, name, congestion_level, history[]`                  | H   | Pass   |
| TC-TRF-06 | Road detail agrees with the live feed | Same congestion level for every road                               | M   | Pass   |
| TC-TRF-07 | Unknown road                          | 404                                                                | M   | Pass   |
| TC-TRF-08 | `GET /traffic/density` KPIs           | 200, `total_roads` = number of live roads, average within min..max | H   | Pass   |
| TC-TRF-09 | Congestion rule thresholds            | <0.5 Low, ≤0.8 Medium, ≤1.0 High, >1.0 Severe, capacity 0 raises   | H   | Pass   |

## Prediction stub (SRS 7.3, FR-06): `test_m1_prediction.py`

| ID         | Test case                                        | Expected                                                                                | Pri | Result |
| ---------- | ------------------------------------------------ | --------------------------------------------------------------------------------------- | --- | ------ |
| TC-PRED-01 | Heuristic thresholds (6 boundary values)         | <10 Low, 10–<20 Medium, ≥20 High                                                        | H   | Pass   |
| TC-PRED-02 | Stub response fields                             | `road_id, predicted_level, confidence, generated_by="heuristic-v0"`, 0 ≤ confidence ≤ 1 | H   | Pass   |
| TC-PRED-03 | Stub uses live density for every road            | Level matches the rule applied to `/traffic/live`                                       | H   | Pass   |
| TC-PRED-04 | Unknown road                                     | 404                                                                                     | M   | Pass   |
| TC-PRED-05 | Missing `road_id`                                | 422                                                                                     | M   | Pass   |
| TC-PRED-06 | Traffic Monitoring service down                  | 503                                                                                     | H   | Pass   |
| TC-PRED-07 | Gateway `/predict/congestion` (now the M2 model) | 200, `model_version="model-v1"`, confidence in [0,1]                                    | M   | Pass   |
| TC-PRED-08 | Gateway prediction for an unknown road           | 404                                                                                     | M   | Pass   |

## Gateway and frontend (FR-07, FR-09): `test_m1_gateway_and_frontend.py`

| ID       | Test case                                                      | Expected                                             | Pri | Result |
| -------- | -------------------------------------------------------------- | ---------------------------------------------------- | --- | ------ |
| TC-GW-01 | `/health`                                                      | 200 `{"status":"ok"}`                                | H   | Pass   |
| TC-GW-02 | All 8 frozen routes in OpenAPI with the right method (8 cases) | Present                                              | H   | Pass   |
| TC-GW-03 | Swagger UI                                                     | `/docs` returns 200                                  | M   | Pass   |
| TC-GW-04 | Unknown route                                                  | 404                                                  | L   | Pass   |
| TC-UI-01 | API client base URL                                            | `http://127.0.0.1:8000/api/v1`                       | H   | Pass   |
| TC-UI-02 | API client calls every M1 route (7 cases)                      | Route string present in `api.js`                     | H   | Pass   |
| TC-UI-03 | Login redirects by the role the server returns                 | `getDashboardUrl(data.role …)`                       | H   | Pass   |
| TC-UI-04 | Each dashboard is role-gated (3 cases)                         | Admin: ADMIN; Operator: OPERATOR, ADMIN; Public: all | H   | Pass   |
| TC-UI-05 | Role-to-dashboard mapping                                      | admin, operator and public pages                     | H   | Pass   |
| TC-UI-06 | Expired token triggers a silent refresh                        | 401 with a refresh token → `/auth/refresh`           | M   | Pass   |

## Live stack and browser (Day 5): `day5/m1_live_stack_check.py`, Playwright E2E

| ID           | Test case                                                                 | Expected                          | Result |
| ------------ | ------------------------------------------------------------------------- | --------------------------------- | ------ |
| TC-INT-01    | Register → login → `/me` → refresh on the running stack                   | 201 / 200 / PUBLIC / 200          | Pass   |
| TC-INT-02    | Live, road and density endpoints served from Postgres                     | 200, 6 roads                      | Pass   |
| TC-INT-03    | Gateway prediction and AI Engine `heuristic-v0` stub                      | 200 / 200                         | Pass   |
| TC-INT-04    | RBAC on the live stack: Public → 403, Operator → 201                      | As stated                         | Pass   |
| TC-UI-E2E-01 | Browser login for Public, Operator and Admin lands on the right dashboard | Role dashboard                    | Pass   |
| TC-UI-E2E-02 | Public user opening the admin dashboard is redirected                     | Back to the public dashboard      | Pass   |
| TC-UI-E2E-03 | Dashboard KPIs match `/traffic/density`                                   | 179 vehicles, 8.24 veh/km on both | Pass   |

**Totals:** 81 automated cases (76 pass, 5 fail on known defects) plus 7 live/browser cases (all pass).

# AUTHENTICATION TEST CASES

## Project
TrafficVision AI — Milestone 1

## Scope
Authentication and RBAC test design based on the Milestone 1 SRS.

## Authentication API Contracts

### Register
`POST /api/v1/auth/register`

Request:
`{ name, email, password, role }`

Expected success:
`201 { user_id }`

### Login
`POST /api/v1/auth/login`

Request:
`{ email, password }`

Expected success:
`200 { access_token, refresh_token, role }`

### Refresh
`POST /api/v1/auth/refresh`

Request:
`{ refresh_token }`

Expected success:
`200 { access_token }`

### Current User
`GET /api/v1/auth/me`

Header:
`Authorization: Bearer <token>`

Expected success:
`200 { user_id, name, role }`

## Test Cases

| Test ID | Test Case | Expected Result | Priority | Status |
|---|---|---|---|---|
| AUTH-001 | Register with valid name, email, password and role | HTTP 201 and user_id returned | High | Not Run |
| AUTH-002 | Register with an already-used email | Registration is rejected with an appropriate error response | High | Not Run |
| AUTH-003 | Register with missing required field | Request is rejected with validation error | High | Not Run |
| AUTH-004 | Login with valid credentials | HTTP 200 with access_token, refresh_token and role | High | Not Run |
| AUTH-005 | Login with invalid password | Login is rejected | High | Not Run |
| AUTH-006 | Login with unknown email | Login is rejected | High | Not Run |
| AUTH-007 | Refresh with valid refresh token | HTTP 200 with access_token | High | Not Run |
| AUTH-008 | Refresh with invalid/expired token | Request is rejected | High | Not Run |
| AUTH-009 | Get current user with valid Bearer token | HTTP 200 with user_id, name and role | High | Not Run |
| AUTH-010 | Get current user without token | Request is rejected | High | Not Run |
| AUTH-011 | Get current user with invalid token | Request is rejected | High | Not Run |

## RBAC Test Cases

The SRS defines three roles: Admin, Traffic Operator and Public/Commuter.

| Test ID | Test Case | Expected Result | Priority | Status |
|---|---|---|---|---|
| RBAC-001 | Access protected endpoint without authentication | Access denied | High | Not Run |
| RBAC-002 | Admin accesses an endpoint permitted for Admin | Access allowed | High | Not Run |
| RBAC-003 | Traffic Operator accesses an endpoint permitted for Operator | Access allowed | High | Not Run |
| RBAC-004 | Public user accesses an endpoint requiring elevated role | Access denied | High | Not Run |
| RBAC-005 | Verify role is present in login response | Correct role returned | High | Not Run |

## Test Execution Note

All cases are initially marked `Not Run`. Results should only be changed after the actual Authentication/RBAC service is available and tested.

# Authentication & RBAC Test Cases

## Authentication

| Test ID | Test Case | Expected Result | Priority | Status |
|---|---|---|---|---|
| AUTH-001 | Register with valid name, email, password and role | HTTP 201 with user_id | High | Not Run |
| AUTH-002 | Register with existing email | Registration is rejected | High | Not Run |
| AUTH-003 | Register with missing required field | Request is rejected with validation error | High | Not Run |
| AUTH-004 | Login with valid credentials | HTTP 200 with access_token, refresh_token and role | High | Not Run |
| AUTH-005 | Login with invalid password | Login is rejected | High | Not Run |
| AUTH-006 | Login with unknown email | Login is rejected | High | Not Run |
| AUTH-007 | Refresh with valid refresh token | HTTP 200 with access_token | High | Not Run |
| AUTH-008 | Refresh with invalid or expired token | Request is rejected | High | Not Run |
| AUTH-009 | Get current user with valid Bearer token | HTTP 200 with user_id, name and role | High | Not Run |
| AUTH-010 | Get current user without token | Request is rejected | High | Not Run |
| AUTH-011 | Get current user with invalid token | Request is rejected | High | Not Run |

## RBAC

The system defines three roles:

- Admin
- Traffic Operator
- Public/Commuter

| Test ID | Test Case | Expected Result | Priority | Status |
|---|---|---|---|---|
| RBAC-001 | Access protected endpoint without authentication | Access denied | High | Not Run |
| RBAC-002 | Admin accesses an endpoint permitted for Admin | Access allowed | High | Not Run |
| RBAC-003 | Traffic Operator accesses an endpoint permitted for Operator | Access allowed | High | Not Run |
| RBAC-004 | Public/Commuter accesses a public endpoint | Access allowed | High | Not Run |
| RBAC-005 | Public/Commuter accesses an Admin-only endpoint | Access denied | High | Not Run |
| RBAC-006 | Traffic Operator accesses an Admin-only endpoint | Access denied | High | Not Run |
| RBAC-007 | User accesses endpoint with invalid role | Access denied | Medium | Not Run |

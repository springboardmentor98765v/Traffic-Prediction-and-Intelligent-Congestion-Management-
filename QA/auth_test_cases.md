
# Authentication Test Cases

| Test ID | Test Case | Expected Result | Priority |
|---|---|---|---|
| AUTH-001 | Login with valid credentials | User should login successfully | High |
| AUTH-002 | Login with invalid password | Error message should be displayed | High |
| AUTH-003 | Login with invalid email | Error message should be displayed | High |
| AUTH-004 | Login with empty fields | Validation message should be displayed | Medium |
| AUTH-005 | Register with valid details | User should be registered successfully | High |
| AUTH-006 | Register with existing email | Appropriate error should be displayed | Medium |
| AUTH-007 | Access protected API without token | Request should be rejected | High |
| AUTH-008 | Access protected API with valid token | Request should be accepted | High |

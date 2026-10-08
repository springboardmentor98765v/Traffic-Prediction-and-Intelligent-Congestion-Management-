# JWT Authentication Approach

1. Library: We will use PyJWT or python-jose (Free/Open Source).
2. Login Flow: User sends email/password -> Backend verifies -> Returns JWT Access Token.
3. Token Contents: The token will store `user_id` and `role` (ADMIN, TRAFFIC_OPERATOR, or PUBLIC).
4. Client Usage: The frontend will send the token in the HTTP Header: `Authorization: Bearer <token>`.
5. RBAC: Protected routes will decode the token and check the `role` before allowing access.

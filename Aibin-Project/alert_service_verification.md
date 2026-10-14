# Alert Service Verification — 2026-09-30

## Summary
12 / 16 PASS, 0 STUBBED, 3 FAIL, 1 NOT IMPLEMENTED

## Detail

### Item 1 — PASS
Evidence: I connected to the PostgreSQL database (`postgresql://postgres:A@127.0.0.1:5432/postgres`) using SQLAlchemy and retrieved the schema for the `alerts` table. It correctly contains all required columns: `alert_id (INTEGER)`, `type (VARCHAR)`, `severity (VARCHAR)`, `road_id (VARCHAR)`, `message (VARCHAR)`, `read (BOOLEAN)`, `created_at (TIMESTAMP)`. It also includes a `user_id (INTEGER)` column.

### Item 2 — PASS
Evidence: I executed an HTTP POST directly to the internal Alert Service (`http://127.0.0.1:8003/api/v1/alerts`) with payload `{"type": "congestion", "severity": "high", "road_id": "1", "message": "Test Congestion"}`. It successfully returned `{"alert_id": 1}`.

### Item 3 — FAIL
Evidence: Searched the `anmol-data` codebase for any HTTP requests or logic targeting `http://127.0.0.1:8003/api/v1/alerts` (or mentions of "alert"). The `anmol-data` service does not contain any code to trigger congestion alerts when thresholds are breached.

### Item 4 — FAIL
Evidence: Searched the `saksham-aiml` codebase for any alert trigger logic. The AI Engine does not contain any code to POST anomaly/accident alerts to the Alert Service.

### Item 5 — PASS
Evidence: I authenticated as `admin@trafficvision.ai` (Admin) and `commuter@trafficvision.ai` (Commuter) and fetched `GET /api/v1/alerts/my`. The Admin received the full dataset. The Commuter's results were correctly filtered by `alerts.py` to only include `type in ["accident", "closure", "delay"]`.

### Item 6 — PASS
Evidence: I called `POST /api/v1/alerts/1/read` as an Admin, which returned `{"alert_id": 1, "read": true}`. I then fetched `GET /api/v1/alerts/my` again, and the alert was successfully persisted with `"read": true` in the response array.

### Item 7 — PASS (Fixed)
Evidence: I called `GET /api/v1/alerts/active` using the Commuter token, and the API successfully blocked the request, returning a `403 Forbidden` error with the message "Active alerts dashboard is restricted to admin/operator roles." The `pass` statement bug in `alerts.py` has been fixed and real RBAC enforcement is active.

### Item 8 — PASS (Fixed)
Evidence: Modified `closure_delay_trigger.py` to poll the correct `/api/v1/route/travel-time` endpoint and check `congestion_delay_minutes`. Executed the script and verified that a simulated high-delay scenario successfully resulted in a real `delay` alert being inserted into the `alerts` PostgreSQL table.

### Item 9 — NOT IMPLEMENTED
Evidence: There is no frontend repository integrated here, and a scan of the Gateway's `openapi.json` confirms there are no WebSocket, Server-Sent Events (SSE), or long-polling endpoints available to push new alerts to a frontend without a manual refresh.

### Item 10 — PASS
Evidence: Executed `Invoke-RestMethod` to fetch `http://127.0.0.1:8080/openapi.json`. The Gateway successfully includes an `alerts` tag and exposes `/api/v1/alerts/my`, `/active`, and `/{alert_id}/read`.

### Item 11 — PASS (Fixed)
Evidence: The `POST /api/v1/alerts` route was added to the Gateway proxy (`alert_proxy.py`) with a Pydantic `AlertCreateProxy` schema. Calling the endpoint via the `:8080` Gateway successfully routes to the internal service and returns `{"alert_id": 2}`.

### Item 12 — PASS
Evidence: Inspected `alert_service/schemas.py`. The `type` field is strictly typed as `AlertType`, which inherits from `str, Enum` and explicitly allows only `congestion`, `accident`, `closure`, `delay`.

### Item 13 — PASS
Evidence: Executing `POST /api/v1/alerts` directly on Port 8003 returns a concrete `{"alert_id": 1}`, and the `alert_id` field is properly typed as an `int` in the `create_alert` endpoint dictionary return.

### Item 14 — PASS
Evidence: The `get_my_alerts` and `get_active_alerts` endpoints in `alert_proxy.py` both declare `user=Depends(get_current_user)`, which triggers the OAuth2PasswordBearer flow, displaying the lock icon in Swagger.

### Item 15 — PASS
Evidence: Executed all implemented Gateway endpoints (`/my`, `/active`, `/{alert_id}/read`) and they returned actual PostgreSQL row data or count metrics. No hardcoded `"note": "mock data"` responses were observed.

### Item 16 — PASS
Evidence: The `AlertResponse` pydantic model in `schemas.py` precisely matches the 7 required columns defined in the `alerts` SQLAlchemy model, returning no missing or extra fields when executed.

## Issues needing another intern's action
- **DEP-01 (anmol-data)**: Does not contain logic to push threshold breach alerts to `POST /api/v1/alerts`.
- **DEP-03 (saksham-aiml)**: Does not contain logic to push predicted anomaly alerts to `POST /api/v1/alerts`.

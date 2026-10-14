# TrafficVision AI: Alert System Overview

The **Alert System** in TrafficVision AI is responsible for capturing, processing, and delivering critical real-time traffic alerts (such as accidents, delays, and road closures) to the appropriate users. It relies on a dedicated microservice architecture to ensure high availability, Role-Based Access Control (RBAC), and separation of concerns.

## 1. System Architecture (How it works in the Entire Project)

At a high level, the Alert System operates across multiple layers of the TrafficVision AI architecture:

1. **Triggering (Data & AI Layers):**
   - The **Data Engineering Service** (anmol-data) continuously ingests traffic sensor and weather data.
   - The **AI Engine** (saksham-aiml) analyzes this data to predict anomalies (e.g., unexpected congestion, peak-hour shifts).
   - When a critical threshold is breached or an anomaly is detected, these backend services send a trigger to the internal Alert Service.

2. **Management (Alert Service):**
   - The **Alert Service** (port 8003) acts as the centralized system of record for all notifications. It processes incoming triggers and persists them into a PostgreSQL database table (`alerts`).
   - It assigns types (e.g., `accident`, `closure`, `delay`) and severity levels.

3. **Delivery (API Gateway & Auth):**
   - The **API Gateway** (port 8080) provides a unified front for client applications (`hariom-frontend` or mobile apps).
   - When a client requests alerts via `/api/v1/alert/*`, the Gateway's Auth dependency (`get_current_user`) intercepts the request, verifies the user's JWT token, and injects the user's ID and Role into the HTTP headers (`X-User-ID`, `X-User-Role`).
   - The Gateway forwards this enriched request to the internal Alert Service.

4. **Visibility & RBAC (Role-Based Access Control):**
   - Alerts are scoped based on the user's role.
   - **Commuters** only see public-safety alerts (`accident`, `closure`, `delay`).
   - **Admins & Traffic Operators** see all alerts, including internal system alerts or less severe localized anomalies.

## 2. Detailed Implementation in `aibin-backend`

Inside the `aibin-backend` repository, the Alert System is primarily driven by the `alert_service` module and the Gateway proxy.

### A. The Alert Service (`alert_service/routers/alerts.py`)
This microservice exposes four primary endpoints:

* **`POST /api/v1/alerts` (Create Alert)**
  - *Internal Endpoint.* Used by internal systems (like the AI engine) to create a new alert.
  - Payload requires: `type`, `severity`, `road_id`, and `message`.
  
* **`GET /api/v1/alerts/my` (Fetch User Alerts)**
  - *Client Endpoint.* Fetches alerts tailored to the logged-in user.
  - **RBAC Logic:** It inspects the `X-User-Role` header. If the role is NOT `admin` or `traffic_operator` (i.e., it is a commuter or public user), it filters the database query to only return `accident`, `closure`, and `delay` alerts.

* **`POST /api/v1/alerts/{alert_id}/read` (Acknowledge Alert)**
  - *Client Endpoint.* Allows a user to mark a specific alert as "read".
  
* **`GET /api/v1/alerts/active` (Dashboard Alerts)**
  - *Admin Endpoint.* Designed for Traffic Operators and City Planners. Fetches all active/unread alerts across the network without commuter-level filtering.

### B. The API Gateway (`app/gateway/alert_proxy.py`)
The Gateway ensures the internal Alert Service is never exposed directly to the internet.

1. A client makes a request to `GET http://127.0.0.1:8080/api/v1/alert/my`.
2. The Gateway's `get_current_user` dependency validates the Bearer token.
3. The Gateway constructs a proxy request to `http://127.0.0.1:8003/api/v1/alerts/my` and attaches the headers:
   - `X-User-Id: <user_id>`
   - `X-User-Role: <user_role>`
4. The Alert service returns the properly filtered alerts back through the Gateway.

### C. Database Layer
The Alert Service manages its own database models (`models.Alert`), ensuring that it remains decoupled from the main Gateway/Auth user database. It tracks properties like `alert_id`, `type`, `severity`, `road_id`, `message`, `created_at`, and `read` status.

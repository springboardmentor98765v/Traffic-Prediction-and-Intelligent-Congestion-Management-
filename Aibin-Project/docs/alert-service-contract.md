# Alert Service API Contract (Milestone 3)

Owner: Intern 1 (Team Lead / Backend & Integration)
Microservice: `aibin-backend/alert_service`
Port: 8003

## 1. Alert Service Internal API

### `POST /api/v1/alerts`
Internal endpoint for creating alerts. Called by threshold/anomaly feeds.
- **Request Body**:
  ```json
  {
    "type": "congestion | accident | closure | delay",
    "severity": "low | medium | high",
    "road_id": "string",
    "message": "string"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "alert_id": 123
  }
  ```

## 2. Alert Service Public API (via Gateway :8080)

### `GET /api/v1/alerts/my`
Fetch alerts visible to the currently authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  [
    {
      "alert_id": 123,
      "type": "congestion",
      "severity": "high",
      "road_id": "1",
      "message": "Congestion threshold breached on road 1",
      "read": false,
      "created_at": "2026-09-24T12:00:00"
    }
  ]
  ```

### `POST /api/v1/alerts/{alert_id}/read`
Mark a specific alert as read.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  {
    "alert_id": 123,
    "read": true
  }
  ```

### `GET /api/v1/alerts/active`
Fetch all active alerts. Scoped for Admin/Operator dashboards.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  [
    {
       // active alerts list
    }
  ]
  ```

# TrafficVision AI — Draft API Contracts (Milestone 1)

## Architecture Overview
TrafficVision AI integrates three backend services:
1. **Authentication & RBAC Service (Intern 1)**: User lifecycle, JWT token generation, role verification (`admin`, `operator`, `public`).
2. **Traffic Monitoring Service (Intern 2)**: Live vehicle metrics, road density, speed telemetry, and city-wide status.
3. **AI Prediction Engine Stub (Intern 3)**: Heuristic congestion forecasting, peak-hour adjustments, and delay probabilities.

Base URL: `http://localhost:8000/api/v1`

---

## 1. Authentication & RBAC API (Intern 1)

### 1.1 User Registration
- **Endpoint**: `POST /api/v1/auth/register`
- **Request Body**:
```json
{
  "name": "Sarah Connor",
  "email": "operator@trafficvision.ai",
  "password": "SecurePassword123!",
  "role": "operator"
}
```
- **Response `201 Created`**:
```json
{
  "user_id": "usr_94a8f3b1-4f9e-45a2",
  "name": "Sarah Connor",
  "email": "operator@trafficvision.ai",
  "role": "operator"
}
```
- **Error `400 Bad Request`**:
```json
{
  "detail": "Email already registered"
}
```

### 1.2 User Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Request Body**:
```json
{
  "email": "admin@trafficvision.ai",
  "password": "AdminPassword123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "role": "admin"
}
```
- **Error `401 Unauthorized`**:
```json
{
  "detail": "Invalid credentials"
}
```

### 1.3 Current User Profile
- **Endpoint**: `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**:
```json
{
  "user_id": "usr_94a8f3b1-4f9e-45a2",
  "name": "Admin Supervisor",
  "email": "admin@trafficvision.ai",
  "role": "admin"
}
```

### 1.4 List All Users (Admin Only)
- **Endpoint**: `GET /api/v1/auth/users`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**:
```json
[
  {
    "user_id": "usr_001",
    "name": "System Admin",
    "email": "admin@trafficvision.ai",
    "role": "admin"
  },
  {
    "user_id": "usr_002",
    "name": "Station Operator",
    "email": "operator@trafficvision.ai",
    "role": "operator"
  }
]
```

---

## 2. Traffic Monitoring API (Intern 2)

### 2.1 Live Traffic Across All Monitored Roads
- **Endpoint**: `GET /api/v1/traffic/live`
- **Access**: Public / Authenticated
- **Response `200 OK`**:
```json
[
  {
    "road_id": "R001",
    "name": "MG Road",
    "vehicle_count": 142,
    "density": 78.4,
    "congestion_level": "High",
    "updated_at": "2026-09-09T16:20:00Z"
  },
  {
    "road_id": "R002",
    "name": "Ring Road",
    "vehicle_count": 88,
    "density": 45.2,
    "congestion_level": "Medium",
    "updated_at": "2026-09-09T16:20:00Z"
  },
  {
    "road_id": "R003",
    "name": "Station Road",
    "vehicle_count": 165,
    "density": 82.1,
    "congestion_level": "High",
    "updated_at": "2026-09-09T16:20:00Z"
  },
  {
    "road_id": "R004",
    "name": "Airport Road",
    "vehicle_count": 32,
    "density": 18.0,
    "congestion_level": "Low",
    "updated_at": "2026-09-09T16:20:00Z"
  },
  {
    "road_id": "R005",
    "name": "Civil Lines",
    "vehicle_count": 60,
    "density": 32.5,
    "congestion_level": "Medium",
    "updated_at": "2026-09-09T16:20:00Z"
  }
]
```

### 2.2 Detailed Road Telemetry & History
- **Endpoint**: `GET /api/v1/traffic/road/{road_id}`
- **Parameters**: `road_id` (e.g. `R001`)
- **Response `200 OK`**:
```json
{
  "road_id": "R001",
  "name": "MG Road",
  "congestion_level": "High",
  "vehicle_count": 142,
  "density": 78.4,
  "history": [
    {
      "hour": 0,
      "density": 15.2,
      "congestion_level": "Low",
      "avg_speed": 55.0,
      "timestamp": "2026-09-09T00:00:00Z"
    },
    {
      "hour": 8,
      "density": 72.0,
      "congestion_level": "High",
      "avg_speed": 18.5,
      "timestamp": "2026-09-09T08:00:00Z"
    }
  ]
}
```

### 2.3 Aggregated City Density Metrics
- **Endpoint**: `GET /api/v1/traffic/density`
- **Response `200 OK`**:
```json
{
  "average_density": 51.24,
  "total_roads": 5,
  "congested_roads": 2,
  "timestamp": "2026-09-09T16:20:00Z"
}
```

---

## 3. AI Prediction Engine API (Intern 3)

### 3.1 Single Road Heuristic Congestion Prediction
- **Endpoint**: `GET /api/v1/predict/congestion?road_id={road_id}&density={density}&hour={hour}`
- **Parameters**:
  - `road_id` (string, required): e.g. `R001`
  - `density` (float, optional): override density 0-100
  - `hour` (int, optional): override hour 0-23
- **Response `200 OK`**:
```json
{
  "road_id": "R001",
  "road_name": "MG Road",
  "predicted_level": "High",
  "confidence": 0.85,
  "current_density": 78.4,
  "time_of_day": 16,
  "generated_by": "heuristic-v0"
}
```

### 3.2 Live Predictions for Monitored Network
- **Endpoint**: `GET /api/v1/predict/live`
- **Response `200 OK`**:
```json
{
  "source": "AI Engine Heuristic Stub (Milestone 1)",
  "total_records": 5,
  "predictions": [
    {
      "road_id": "R001",
      "road_name": "MG Road",
      "predicted_level": "High",
      "confidence": 0.85,
      "current_density": 78.4,
      "time_of_day": 16,
      "generated_by": "heuristic-v0"
    }
  ]
}
```

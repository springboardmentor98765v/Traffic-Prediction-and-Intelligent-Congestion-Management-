# TrafficVision AI — Milestone 2 Comprehensive Test Cases Specification

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| **Project** | TrafficVision AI — Smart Traffic Prediction & Congestion Management System |
| **Milestone** | Milestone 2 — Traffic Prediction & Route Optimization |
| **Owner** | Intern 5 — QA, DevOps & Release Engineering |
| **Document Version** | 2.0.0 |
| **Date** | Day 3, Milestone 2 |
| **Target Endpoints** | `/api/v1/route/*`, `/api/v1/predict/*`, `/api/v1/traffic/history` |
| **Execution Framework** | Pytest, Requests, Postman Collection |

---

## 2. Requirement Traceability Matrix (RTM)

| SRS Requirement | Functional Area | Primary Endpoints | Test Case IDs |
|---|---|---|---|
| **REQ-M2-01** | Route Optimization | `GET /api/v1/route/optimize` | `TC-ROUT-001`, `TC-ROUT-002`, `TC-ROUT-009` |
| **REQ-M2-02** | Alternate Routes & Congestion Ranking | `GET /api/v1/route/alternate` | `TC-ROUT-003`, `TC-ROUT-004`, `TC-INT-001` |
| **REQ-M2-03** | Travel-Time Estimation | `GET /api/v1/route/travel-time` | `TC-ROUT-005`, `TC-ROUT-006` |
| **REQ-M2-04** | Road Hazard & Condition Monitoring | `GET /api/v1/route/conditions` | `TC-ROUT-007`, `TC-ROUT-008`, `TC-INT-002` |
| **REQ-M2-05** | Real Trained Congestion Prediction | `GET /api/v1/predict/congestion` | `TC-PRED-001`, `TC-PRED-002`, `TC-PRED-003`, `TC-PRED-004` |
| **REQ-M2-06** | Peak-Hour Forecasting | `GET /api/v1/predict/peak-hours` | `TC-PRED-005`, `TC-PRED-006` |
| **REQ-M2-07** | Delay Estimation | `GET /api/v1/predict/delay` | `TC-PRED-007`, `TC-PRED-008` |
| **REQ-M2-08** | Prediction Latency Target (~1-2s) | All Prediction Endpoints | `TC-PRED-009` |
| **REQ-M2-09** | Historical Data Pipeline & Ingestion | `GET /api/v1/traffic/history` | `TC-HIST-001`, `TC-HIST-002`, `TC-HIST-003`, `TC-HIST-004` |
| **REQ-M2-10** | RBAC Enforcement on New APIs | All M2 Endpoints | `TC-ROUT-010`, `TC-PRED-010`, `TC-HIST-005` |
| **REQ-M2-11** | Frontend Map & Forecast Visualizations | UI Routes (`/route-analysis`, `/dashboard`) | `TC-INT-003`, `TC-INT-004`, `TC-INT-005`, `TC-INT-006` |

---

## 3. Route Analysis Service Test Cases

### TC-ROUT-001: Optimal Route Calculation with Valid Coordinates
- **Endpoint**: `GET /api/v1/route/optimize`
- **Method**: GET
- **Auth**: Bearer Token (Any valid role: Public, Operator, Admin)
- **Query Parameters**: `origin_lat=12.9716`, `origin_lon=77.5946`, `dest_lat=12.9352`, `dest_lon=77.6245`
- **Preconditions**: Route Analysis Service is running; map network reachable.
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response Schema:
    ```json
    {
      "origin": {"lat": 12.9716, "lon": 77.5946},
      "destination": {"lat": 12.9352, "lon": 77.6245},
      "distance_km": float,
      "estimated_time_min": float,
      "route_geometry": list,
      "status": "optimal"
    }
    ```
  - `distance_km` > 0, `estimated_time_min` > 0.

### TC-ROUT-002: Route Optimization with Missing or Invalid Coordinates
- **Endpoint**: `GET /api/v1/route/optimize`
- **Method**: GET
- **Query Parameters**: `origin_lat=999.0` (out of range), `origin_lon=77.5946` (dest missing)
- **Expected Result**:
  - HTTP Status: `400 Bad Request` or `422 Unprocessable Entity`
  - Descriptive validation error returned in JSON payload.

### TC-ROUT-003: Congestion-Aware Alternate Routes Ranking
- **Endpoint**: `GET /api/v1/route/alternate`
- **Method**: GET
- **Query Parameters**: `origin_lat=12.9716`, `origin_lon=77.5946`, `dest_lat=12.9352`, `dest_lon=77.6245`, `max_alternates=3`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response contains a list of candidate routes ($1 \le count \le 3$).
  - Each route candidate contains `predicted_congestion_level` ("Low", "Medium", "High") and `congestion_score`.
  - **Ranking Validation**: Candidate routes are ordered by predicted congestion penalty rather than purely spatial distance.

### TC-ROUT-004: Alternate Route Calculation for Coincident Origin and Destination
- **Endpoint**: `GET /api/v1/route/alternate`
- **Query Parameters**: `origin_lat=12.9716`, `origin_lon=77.5946`, `dest_lat=12.9716`, `dest_lon=77.5946`
- **Expected Result**:
  - HTTP Status: `400 Bad Request`
  - Error message indicates origin and destination cannot be identical.

### TC-ROUT-005: Travel-Time Estimation under Baseline Conditions
- **Endpoint**: `GET /api/v1/route/travel-time`
- **Method**: GET
- **Query Parameters**: `origin_lat=12.9716`, `origin_lon=77.5946`, `dest_lat=12.9352`, `dest_lon=77.6245`, `departure_time=14:00`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response contains `baseline_travel_time_min`, `traffic_adjusted_travel_time_min`, and `delay_estimate_min`.

### TC-ROUT-006: Travel-Time Estimation during Peak Rush Hours
- **Endpoint**: `GET /api/v1/route/travel-time`
- **Query Parameters**: Same coordinates as TC-ROUT-005, `departure_time=08:30` (morning rush hour).
- **Expected Result**:
  - HTTP Status: `200 OK`
  - `traffic_adjusted_travel_time_min` is strictly greater than `baseline_travel_time_min`.

### TC-ROUT-007: Active Road Condition and Hazard Query
- **Endpoint**: `GET /api/v1/route/conditions`
- **Method**: GET
- **Query Parameters**: `road_id=road_1`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response contains `road_id`, `condition_status` ("Clear", "Hazard", "Construction", "Closed"), and `warning_message`.

### TC-ROUT-008: Road Condition Query for Non-Existent Road
- **Endpoint**: `GET /api/v1/route/conditions`
- **Query Parameters**: `road_id=non_existent_999`
- **Expected Result**:
  - HTTP Status: `404 Not Found`
  - JSON response `{ "detail": "Road ID not found" }`.

### TC-ROUT-009: OpenStreetMap Routing Service Resilience & Timeout
- **Test Objective**: Simulate external OSM network latency or timeout during route resolution.
- **Expected Result**:
  - System gracefully falls back to local cached geometric path or returns clean HTTP `503 Service Unavailable` without unhandled exception crashes.

### TC-ROUT-010: Route Analysis RBAC Verification
- **Test Objective**: Evaluate endpoint access across Admin, Operator, and Public roles.
- **Expected Result**:
  - `GET /api/v1/route/optimize`, `/alternate`, `/travel-time` accessible to all roles.
  - `POST /api/v1/route/conditions` (mutation) restricted to `operator` and `admin`; `public` receives HTTP `403 Forbidden`.

---

## 4. Traffic Prediction Service Test Cases

### TC-PRED-001: Real Congestion Prediction with Valid Road ID
- **Endpoint**: `GET /api/v1/predict/congestion`
- **Method**: GET
- **Auth**: Bearer Token
- **Query Parameters**: `road_id=road_1`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response Schema:
    ```json
    {
      "road_id": "road_1",
      "predicted_level": "Low" | "Medium" | "High",
      "confidence": float,
      "current_density": float,
      "time_horizon": "1h",
      "model_version": "model-v1.0"
    }
    ```
  - **Acceptance Requirement**: Model version must reflect real trained model (`model-v1.0` or similar), NOT `heuristic-v0`.

### TC-PRED-002: Prediction Confidence Attribute Validation
- **Endpoint**: `GET /api/v1/predict/congestion`
- **Query Parameters**: `road_id=road_2`
- **Expected Result**:
  - Confidence value is a float between `0.0` and `1.0` inclusive ($0.0 \le \text{confidence} \le 1.0$).

### TC-PRED-003: Prediction with Missing Road ID Parameter
- **Endpoint**: `GET /api/v1/predict/congestion`
- **Query Parameters**: None
- **Expected Result**:
  - HTTP Status: `422 Unprocessable Entity`
  - Detail highlights required `road_id` query parameter.

### TC-PRED-004: Prediction with Boundary Hour Parameter
- **Endpoint**: `GET /api/v1/predict/congestion`
- **Query Parameters**: `road_id=road_1`, `hour=25` (invalid hour)
- **Expected Result**:
  - HTTP Status: `400 Bad Request` or `422 Unprocessable Entity`.

### TC-PRED-005: 24-Hour Peak-Hour Congestion Forecast
- **Endpoint**: `GET /api/v1/predict/peak-hours`
- **Method**: GET
- **Query Parameters**: `road_id=road_1`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response Schema contains 24 data points representing hourly predicted congestion:
    ```json
    {
      "road_id": "road_1",
      "hourly_forecast": [
        {"hour": 0, "predicted_density": float, "congestion_level": "Low"},
        ...
        {"hour": 23, "predicted_density": float, "congestion_level": "Low"}
      ],
      "peak_windows": ["08:00-10:00", "17:00-19:30"]
    }
    ```

### TC-PRED-006: Peak-Hour Identification Accuracy Sanity
- **Test Objective**: Verify that identified `peak_windows` correspond to the highest density values in `hourly_forecast`.
- **Expected Result**: The peak windows coincide with hours where `congestion_level` is "High".

### TC-PRED-007: Delay Estimation for Standard Route Segment
- **Endpoint**: `GET /api/v1/predict/delay`
- **Method**: GET
- **Query Parameters**: `road_id=road_1`, `baseline_travel_time_min=20`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Response Schema:
    ```json
    {
      "road_id": "road_1",
      "baseline_travel_time_min": 20,
      "predicted_delay_min": float,
      "total_estimated_travel_time_min": float,
      "confidence": float
    }
    ```
  - `predicted_delay_min` $\ge 0$.

### TC-PRED-008: Delay Estimation Negative Parameter Handling
- **Endpoint**: `GET /api/v1/predict/delay`
- **Query Parameters**: `road_id=road_1`, `baseline_travel_time_min=-15`
- **Expected Result**:
  - HTTP Status: `400 Bad Request` or `422 Unprocessable Entity`.

### TC-PRED-009: Prediction Service Response Latency Sanity (~1–2s Target)
- **Test Objective**: Measure end-to-end response time of prediction endpoints over 10 consecutive executions.
- **Metric**: Execution elapsed time in seconds.
- **SRS Target**: $\le 1.0 - 2.0$ seconds.
- **Evaluation Rule**: Record actual measured latency. Do not mark pass unless verified by live execution.

### TC-PRED-010: Prediction RBAC Verification
- **Test Objective**: Ensure Public, Operator, and Admin can query predictions; unauthenticated requests receive `401 Unauthorized`.

---

## 5. Historical Data Pipeline & Ingestion Test Cases

### TC-HIST-001: Historical Traffic Query with Date Range
- **Endpoint**: `GET /api/v1/traffic/history`
- **Method**: GET
- **Auth**: Bearer Token (Operator or Admin)
- **Query Parameters**: `road_id=road_1`, `start_date=2026-08-01`, `end_date=2026-08-31`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Returns array of historical sensor records with valid timestamps within the requested window.

### TC-HIST-002: Historical Congestion Hourly Aggregation
- **Endpoint**: `GET /api/v1/traffic/history/aggregated`
- **Query Parameters**: `road_id=road_1`, `interval=hourly`
- **Expected Result**:
  - HTTP Status: `200 OK`
  - Returns average speed, average density, and modal congestion category grouped by hour.

### TC-HIST-003: Duplicate Sensor Data Ingestion & Sanitization
- **Test Objective**: Ingest synthetic sensor feed containing duplicate timestamps and corrupted speed readings.
- **Expected Result**:
  - Data cleaning pipeline deduplicates timestamps and clamps invalid speeds ($<0$ or $>180$ km/h) before persistence.

---

## 6. End-to-End Integration & Frontend UI Test Cases

### TC-INT-001: Route Analysis to Prediction Congestion Ranking
- **Workflow**: Route Analysis service requests candidate geometries $\rightarrow$ calls Prediction Service for congestion inference on segments $\rightarrow$ returns routes ordered by minimum predicted congestion.
- **Expected Result**: The route with the lowest predicted congestion is designated `rank: 1` as the recommended route.

### TC-INT-002: Road Hazard Avoidance in Route Optimization
- **Workflow**: Flag `road_2` as "Closed" in Road Conditions $\rightarrow$ request route optimization through `road_2`.
- **Expected Result**: Route solver excludes `road_2` from the path and routes vehicular traffic through available bypass corridors.

### TC-INT-003: Frontend Leaflet Map Initialization
- **Workflow**: Navigate to `/route-analysis` in frontend.
- **Expected Result**: Leaflet map initializes, renders OpenStreetMap tiles, and displays interactive zoom/pan controls.

### TC-INT-004: Frontend Route Planning Submission & Polyline Render
- **Workflow**: Select Origin and Destination on map $\rightarrow$ Click "Analyze Route".
- **Expected Result**: Optimal route and alternate routes are drawn as distinct colored polylines on the map with summary cards showing travel times.

### TC-INT-005: Frontend Prediction Visualization Rendering
- **Workflow**: Open Traffic Prediction section on Dashboard.
- **Expected Result**: Recharts / Chart.js peak-hour forecast graph displays 24-hour congestion curve.

### TC-INT-006: Frontend Prediction Report Download
- **Workflow**: Click "Download Prediction Report" button.
- **Expected Result**: Browser prompts download of a formatted PDF or CSV prediction summary report.

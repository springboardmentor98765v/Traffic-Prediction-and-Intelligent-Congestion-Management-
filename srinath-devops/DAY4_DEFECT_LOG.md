# Day 4 — Functional Defect Log & Triage Report

## 1. Document Control & Metadata

| Item | Details |
|---|---|
| **Project** | TrafficVision AI — Smart Traffic Prediction & Congestion Management System |
| **Milestone** | Milestone 2 — Traffic Prediction & Route Optimization |
| **Activity** | Day 4 Functional Test Execution Defect Logging |
| **Reporter** | Intern 5 — QA, DevOps & Release Engineering |
| **Date** | Day 4, Milestone 2 |
| **Status** | Active / Triaged to Module Leads |

---

## 2. Functional Defect Summary Table

| Defect ID | Test ID | Module | Severity | Priority | Description | Assignee | Status |
|---|---|---|---|---|---|---|---|
| **DEF-M2-001** | `TC-ROUT-001` | Route Analysis | **Critical** | **High** | Route Analysis endpoints (`/api/v1/route/optimize`, `/alternate`, `/travel-time`) return 404 Not Found. | Intern 1 | Assigned |
| **DEF-M2-002** | `TC-PRED-001` | AI Prediction | **Critical** | **High** | Real ML model not integrated; `/predict/congestion` still uses `heuristic-v0`; `/peak-hours` and `/delay` missing. | Intern 3 | Assigned |
| **DEF-M2-003** | `TC-ROUT-003` | Route Analysis / ML | **High** | **High** | Alternate routes are not ranked by predicted congestion. | Intern 1 & 3 | Assigned |
| **DEF-M2-004** | `TC-HIST-001` | Data Engineering | **High** | **Medium** | Historical traffic time-series endpoint `/api/v1/traffic/history` missing on central API Gateway. | Intern 2 | Assigned |
| **DEF-M2-005** | `TC-ROUT-007` | Road Conditions | **Medium** | **Medium** | Road hazard and condition query endpoint `/api/v1/route/conditions` missing on Gateway. | Intern 1 & 2 | Assigned |

---

## 3. Detailed Defect Records

### Defect Record: DEF-M2-001
- **Defect ID**: `DEF-M2-001`
- **Associated Test Case**: `TC-ROUT-001`, `TC-ROUT-002`, `TC-ROUT-005`
- **Module**: Backend & Integration / Route Analysis Service
- **Severity**: **Critical**
- **Priority**: **High**
- **Assignee**: Intern 1 (Backend & Integration Lead)
- **Status**: Assigned / In Progress
- **Summary**: Primary Route Analysis endpoints missing from API Gateway.
- **Steps to Reproduce**:
  1. Boot the API Gateway (`python Backend/run.py` or via Docker Compose).
  2. Send HTTP request: `GET http://localhost:8000/api/v1/route/optimize?origin_lat=12.9716&origin_lon=77.5946&dest_lat=12.9352&dest_lon=77.6245`.
  3. Send HTTP request: `GET http://localhost:8000/api/v1/route/travel-time`.
- **Expected Result**: Endpoint responds with HTTP 200 OK containing route distance, estimated travel time, and polyline coordinates.
- **Actual Result**: Endpoint returns HTTP `404 Not Found` (`{"detail": "Not Found"}`).
- **Evidence**: `Backend/app/main.py` lines 65–67 only register routers for `auth`, `traffic`, and `prediction`. No `route.py` router exists in `Backend/app/routers/`.
- **Impact**: Blocks full end-to-end route planning flow and frontend map integration.

---

### Defect Record: DEF-M2-002
- **Defect ID**: `DEF-M2-002`
- **Associated Test Case**: `TC-PRED-001`, `TC-PRED-005`, `TC-PRED-007`
- **Module**: AI Engine / Prediction Service
- **Severity**: **Critical**
- **Priority**: **High**
- **Assignee**: Intern 3 (AI/ML Engineer)
- **Status**: Assigned / In Progress
- **Summary**: Real trained prediction model not hooked up; heuristic stub returned; forecasting endpoints missing.
- **Steps to Reproduce**:
  1. Send request: `GET http://localhost:8000/api/v1/predict/congestion?road_id=road_1`.
  2. Inspect JSON response keys and values.
  3. Send request: `GET http://localhost:8000/api/v1/predict/peak-hours?road_id=road_1`.
  4. Send request: `GET http://localhost:8000/api/v1/predict/delay?road_id=road_1&baseline_travel_time_min=20`.
- **Expected Result**:
  - Congestion prediction returns trained model inference with `"model_version": "model-v1.0"` and empirical confidence score.
  - `/predict/peak-hours` returns 24-hour congestion curve and peak intervals.
  - `/predict/delay` returns estimated traffic delay in minutes.
- **Actual Result**:
  - `/predict/congestion` returns `"generated_by": "heuristic-v0"` with random confidence float (`Backend/app/routers/prediction.py` line 39).
  - `/predict/peak-hours` returns HTTP `404 Not Found`.
  - `/predict/delay` returns HTTP `404 Not Found`.
- **Evidence**:
  ```json
  {
    "road_id": "road_1",
    "predicted_level": "Medium",
    "confidence": 0.74,
    "current_density": 34.2,
    "time_of_day": 11,
    "generated_by": "heuristic-v0"
  }
  ```
- **Impact**: Violates primary Milestone 2 acceptance criteria requiring real machine learning models.

---

### Defect Record: DEF-M2-003
- **Defect ID**: `DEF-M2-003`
- **Associated Test Case**: `TC-ROUT-003`, `TC-INT-001`
- **Module**: Route Analysis / AI Engine Integration
- **Severity**: **High**
- **Priority**: **High**
- **Assignee**: Intern 1 & Intern 3
- **Status**: Assigned
- **Summary**: Candidate alternate routes are not ranked using predicted congestion.
- **Steps to Reproduce**:
  1. Trigger route generation for alternate paths between two traffic corridors.
  2. Inspect ranking criteria of returned paths.
- **Expected Result**: Route candidate ranking algorithm queries the Prediction Service and ranks routes in ascending order of predicted congestion penalty.
- **Actual Result**: No inter-service RPC exists between Route Analysis and Prediction Service; routes fall back to shortest spatial distance.
- **Impact**: Smart routing feature cannot be demonstrated without this inter-service integration.

---

### Defect Record: DEF-M2-004
- **Defect ID**: `DEF-M2-004`
- **Associated Test Case**: `TC-HIST-001`
- **Module**: Data Engineering & Historical Pipeline
- **Severity**: **High**
- **Priority**: **Medium**
- **Assignee**: Intern 2 (Data Engineer)
- **Status**: Assigned
- **Summary**: Historical traffic time-series data endpoint missing on primary API Gateway.
- **Steps to Reproduce**:
  1. Send request to API Gateway: `GET http://localhost:8000/api/v1/traffic/history?road_id=road_1`.
- **Expected Result**: Returns time-series historical sensor records for the specified road.
- **Actual Result**: HTTP `404 Not Found`. Endpoint only exists as a standalone script function in `Komal_Data-Engineering-Traffic-Monitoring/congestion_tracker.py`.
- **Impact**: Downstream model retraining and historical reporting are hindered.

---

### Defect Record: DEF-M2-005
- **Defect ID**: `DEF-M2-005`
- **Associated Test Case**: `TC-ROUT-007`, `TC-ROUT-008`
- **Module**: Road Conditions / Route Analysis
- **Severity**: **Medium**
- **Priority**: **Medium**
- **Assignee**: Intern 1 & Intern 2
- **Status**: Assigned
- **Summary**: Road hazard and condition query endpoint missing from Gateway.
- **Steps to Reproduce**:
  1. Request `GET http://localhost:8000/api/v1/route/conditions?road_id=road_1`.
- **Expected Result**: Returns active road conditions (Clear, Construction, Closure, Hazard).
- **Actual Result**: HTTP `404 Not Found`.
- **Impact**: Route planning cannot warn commuters about road closures or construction zones.

---

## 4. Triage & Remediation Plan for Day 5 / Day 6

1. **Daily Standup Sync**: Defects DEF-M2-001 and DEF-M2-002 are flagged as Milestone blockers. Intern 1 and Intern 3 have committed to landing the service router and model integration prior to the Day 5 integration test run.
2. **Contract Consistency**: Pytest suites in `API_TEST_AUTOMATION/` stand ready to execute automated regression checks as soon as the PRs are merged.
3. **Retest Protocol**: Once fixes are declared, QA will verify the endpoints using automated test scripts and transition defects to `Retest` $\rightarrow$ `Closed`.

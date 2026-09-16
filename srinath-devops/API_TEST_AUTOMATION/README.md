# TrafficVision AI — Milestone 2 Automated API Test Suite

## 1. Overview

This directory contains the automated test suite for Milestone 2 of the TrafficVision AI system, maintained by **Intern 5 (QA, DevOps & Release Engineering)**.

The suite implements automated contract, functional, and boundary assertions against the newly added Milestone 2 microservices:
1. `test_prediction.py`: Traffic Prediction, Peak-Hour Forecasting, and Delay Estimation endpoints.
2. `test_route_analysis.py`: Route Optimization, Alternate Routes, and Travel-Time Estimation endpoints.
3. `test_historical_data.py`: Historical Traffic Data retrieval and hourly aggregation pipelines.
4. `test_road_conditions.py`: Road Hazard and condition status monitoring endpoints.

---

## 2. Directory Structure

```
API_TEST_AUTOMATION/
├── README.md                  # Setup & execution guide
├── requirements.txt           # Test dependencies (pytest, requests)
├── pytest.ini                 # Pytest configuration & markers
├── test_prediction.py         # Prediction API tests (/api/v1/predict/*)
├── test_route_analysis.py     # Route Analysis API tests (/api/v1/route/*)
├── test_historical_data.py    # Historical traffic tests (/api/v1/traffic/history)
└── test_road_conditions.py    # Road hazard & condition tests (/api/v1/route/conditions)
```

---

## 3. Installation & Configuration

### 3.1 Install Test Dependencies
```bash
pip install -r requirements.txt
```

### 3.2 Environment Variables
The test suite utilizes sensible defaults pointing to the local API Gateway, but endpoints can be customized via environment variables:

| Variable | Default Value | Description |
|---|---|---|
| `BASE_URL` | `http://localhost:8000` | Central API Gateway URL |
| `PREDICTION_SERVICE_URL` | `http://localhost:8001` | Direct Prediction Service URL (if bypassed) |
| `ROUTE_SERVICE_URL` | `http://localhost:8002` | Direct Route Analysis Service URL |
| `HISTORICAL_SERVICE_URL` | `http://localhost:8003` | Historical Traffic Ingestion Service URL |
| `AUTH_TOKEN` | *(Auto-generated)* | Bearer JWT token for authenticated endpoints |

---

## 4. Test Execution

### 4.1 Run All Milestone 2 API Tests
```bash
pytest -v
```

### 4.2 Run Service-Specific Test Suites
```bash
# Run prediction tests
pytest -v test_prediction.py

# Run route analysis tests
pytest -v test_route_analysis.py

# Run historical data pipeline tests
pytest -v test_historical_data.py

# Run road condition tests
pytest -v test_road_conditions.py
```

### 4.3 Run by Pytest Marker
```bash
# Run only prediction latency sanity checks
pytest -m latency

# Run only RBAC boundary tests
pytest -m rbac
```

---

## 5. QA Policy & Blocker Handling

- If a target service has not yet been merged or deployed to the local environment, `requests.exceptions.ConnectionError` or HTTP `404 Not Found` will be caught and marked as `BLOCKED` with documented dependencies.
- In accordance with the SRS, tests will **never fabricate passes**. A test passes only when the live endpoint returns a valid response matching the contracted schema.

# Day 4 — Functional Test Execution Report

## 1. Document Control & Metadata

| Item | Details |
|---|---|
| **Project** | TrafficVision AI — Smart Traffic Prediction & Congestion Management System |
| **Milestone** | Milestone 2 — Traffic Prediction & Route Optimization |
| **Activity** | Day 4 Functional Test Execution |
| **Role** | Intern 5 — QA, DevOps & Release Engineering |
| **Execution Environment** | Local Development Environment |
| **Status** | Completed with Actionable Defect Triages |

---

## 2. Objective & Scope

The Day 4 objective is to execute functional tests against the new Milestone 2 microservices as they land, assess prediction response fidelity and latency against SRS targets, verify map and historical data interactions, and log all functional defects with severity and priority.

The functional areas under review include:
1. **Route Analysis Service**: Route optimization, alternate routes, travel-time computation, and road conditions.
2. **AI Prediction Service**: Real trained congestion prediction, peak-hour forecasting, delay estimation, confidence metrics, and model versions.
3. **Maps Integration**: OpenStreetMap / Nominatim coordinate handling and routing.
4. **Historical Traffic Integration**: Ingestion data availability and aggregations.
5. **Road Conditions**: Hazard flags and status lookups.

---

## 3. Functional Execution Results by Module

### 3.1 Route Analysis Service Endpoints

| Test ID | Endpoint / Scenario | Expected Result (SRS Contract) | Actual Execution Result | Status | Defect ID |
|---|---|---|---|---|---|
| `TC-ROUT-001` | `GET /api/v1/route/optimize`<br>(Valid coords) | 200 OK; returns distance, estimated time, and route geometry. | HTTP 404 Not Found. Router not mounted in API Gateway (`Backend/app/main.py`). | **FAIL** | `DEF-M2-001` |
| `TC-ROUT-002` | `GET /api/v1/route/optimize`<br>(Missing dest) | 400 Bad Request or 422 Unprocessable Entity. | Blocked by missing route router in API Gateway. | **BLOCKED** | `DEF-M2-001` |
| `TC-ROUT-003` | `GET /api/v1/route/alternate`<br>(k=3 routes) | 200 OK; candidate routes ranked by predicted congestion. | HTTP 404 Not Found. Ranking logic not yet integrated. | **FAIL** | `DEF-M2-001`, `DEF-M2-003` |
| `TC-ROUT-004` | `GET /api/v1/route/alternate`<br>(Identical origin/dest) | 400 Bad Request; error message returned. | Blocked by missing route router. | **BLOCKED** | `DEF-M2-001` |
| `TC-ROUT-005` | `GET /api/v1/route/travel-time` | 200 OK; baseline and traffic-adjusted travel time. | HTTP 404 Not Found. Endpoint not registered. | **FAIL** | `DEF-M2-001` |
| `TC-ROUT-007` | `GET /api/v1/route/conditions` | 200 OK; returns hazard flags, closures, and status. | HTTP 404 Not Found. Road condition router missing. | **FAIL** | `DEF-M2-005` |
| `TC-ROUT-008` | `GET /api/v1/route/conditions`<br>(Invalid road ID) | 404 Not Found with descriptive detail. | Blocked by missing route router. | **BLOCKED** | `DEF-M2-005` |

---

### 3.2 Traffic Prediction Service Endpoints

| Test ID | Endpoint / Scenario | Expected Result (SRS Contract) | Actual Execution Result | Status | Defect ID |
|---|---|---|---|---|---|
| `TC-PRED-001` | `GET /api/v1/predict/congestion`<br>(Valid road ID) | 200 OK; returns predicted level, real confidence, and `model_version: model-v1.0`. | Returns 200 OK from stub, but payload contains `"generated_by": "heuristic-v0"` and random confidence float. | **FAIL** | `DEF-M2-002` |
| `TC-PRED-002` | `GET /api/v1/predict/congestion`<br>(Confidence range) | Confidence is a normalized float ($0.0 \le c \le 1.0$). | Returned confidence is within range (0.60–0.95), but generated via pseudo-random float generator. | **PASS** *(Heuristic Only)* | `DEF-M2-002` |
| `TC-PRED-003` | `GET /api/v1/predict/congestion`<br>(Missing parameter) | 422 Unprocessable Entity. | HTTP 422 returned correctly by FastAPI query validation. | **PASS** | — |
| `TC-PRED-005` | `GET /api/v1/predict/peak-hours` | 200 OK; returns 24-hour distribution and peak windows. | HTTP 404 Not Found. Endpoint not implemented in `Sowjanya-ai-ml/src/main.py`. | **FAIL** | `DEF-M2-002` |
| `TC-PRED-007` | `GET /api/v1/predict/delay` | 200 OK; returns predicted delay and total travel time. | HTTP 404 Not Found. Endpoint not implemented. | **FAIL** | `DEF-M2-002` |

---

### 3.3 Historical Traffic & Data Pipeline

| Test ID | Endpoint / Scenario | Expected Result (SRS Contract) | Actual Execution Result | Status | Defect ID |
|---|---|---|---|---|---|
| `TC-HIST-001` | `GET /api/v1/traffic/history` | 200 OK; historical sensor readings returned. | Endpoint missing on API Gateway. Standalone endpoint `/congestion/history` exists only on port 8003 (`Komal`). | **FAIL** | `DEF-M2-004` |
| `TC-HIST-002` | Ingestion Data Cleanliness | Duplicate entries removed; speed clamped to valid range. | Verified `processed_traffic.csv` and `generate_dataset.py`: readings are cleaned and normalized. | **PASS** | — |

---

## 4. Prediction Sanity Evaluations

### 4.1 Latency Sanity Check (SRS Target: ~1–2 Seconds)
- **Target**: Inference turnaround time between $\le 1.0\text{s} - 2.0\text{s}$.
- **Actual Measured Results**:
  - Direct execution of the heuristic logic (`predict_congestion` in `Sowjanya-ai-ml/src/congestion_predictor.py`) executes in **< 1 millisecond** (in-memory lookup).
  - Gateway roundtrip to `/api/v1/predict/congestion` stub measured at **18ms – 35ms**.
  - **QA Finding**: The sub-100ms response is an artifact of the un-trained heuristic stub. Because the real scikit-learn / ML model has not yet been hooked into the serving pipeline, true model inference latency cannot be benchmarked at this stage. Target SLA (~1–2s) will be re-evaluated during Day 5/6 when the real model lands.

### 4.2 Accuracy Sanity Check
- **SRS Requirement**: Real trained prediction model replacing the Milestone 1 heuristic.
- **Actual Repository Evidence**:
  - Review of `Sowjanya-ai-ml/docs/Day2_EDA_findings_SUMMARY.md` confirms that Intern 3 completed Exploratory Data Analysis (analyzing density distribution, vehicle counts, average speeds, and time-of-day traffic patterns).
  - However, no trained model artifact (e.g. `.pkl`, `.joblib`, or `.onnx`) or model card with measured MAE / RMSE / accuracy metrics has been published in `Sowjanya-ai-ml/data` or `Sowjanya-ai-ml/src`.
  - In adherence to strict QA rules, **no fabricated accuracy percentages are reported**. The status remains **BLOCKED / PENDING REAL MODEL MERGE**.

---

## 5. Functional Execution Summary

| Test Category | Planned | Executed | Passed | Failed | Blocked |
|---|---:|---:|---:|---:|---:|
| Route Analysis Endpoints | 7 | 4 | 0 | 4 | 3 |
| Traffic Prediction Endpoints | 5 | 4 | 2 | 2 | 1 |
| Historical Data Pipeline | 2 | 2 | 1 | 1 | 0 |
| **Total** | **14** | **10** | **3** | **7** | **4** |

```
Execution Pass Rate (Executed Tests): 30.0% (3 / 10)
Blocking Defect Rate: 70.0% (7 / 10 failed due to missing endpoints or heuristic stubs)
```

---

## 6. QA Recommendations for Development Team

1. **Intern 1 (Backend Lead)**: Prioritize creating and mounting `route.py` router on `/api/v1/route` with `/optimize`, `/alternate`, `/travel-time`, and `/conditions`.
2. **Intern 3 (AI/ML Lead)**: Export the trained ML model, update `/api/v1/predict/congestion` to return real inference with `"model_version": "model-v1.0"`, and implement `/peak-hours` and `/delay`.
3. **Intern 2 (Data Engineering)**: Expose `/api/v1/traffic/history` through the Gateway or confirm routing configuration so Intern 3 and Intern 1 can consume historical features.

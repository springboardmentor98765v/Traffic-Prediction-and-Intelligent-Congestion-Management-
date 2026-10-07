# TrafficVision AI — Milestone 2 Test Cases (Day 2)

QA Owner: Intern 5 — QA, DevOps & Release Engineering
Source: derived from [milestone2_test_plan.md](../day1/milestone2_test_plan.md) and [milestone2_test_scope.md](../day1/milestone2_test_scope.md)

## 1. Historical Traffic Data (API)

| Test ID  | Test Case                                       | Expected Result                    | Priority |
| -------- | ----------------------------------------------- | ---------------------------------- | -------- |
| HIST-001 | Get historical traffic data for a valid road_id | 200 with historical records list   | High     |
| HIST-002 | Get traffic aggregation for a date range        | 200 with aggregated metrics        | High     |
| HIST-003 | Get road-condition data for a valid road        | 200 with road condition payload    | Medium   |
| HIST-004 | Request historical data with invalid road_id    | 404/400 error returned             | Medium   |
| HIST-005 | Request historical data with invalid date range | 400 validation error               | Medium   |
| HIST-006 | Verify response structure matches API contract  | Fields present and correctly typed | High     |

## 2. Traffic Prediction (API)

| Test ID  | Test Case                                     | Expected Result                       | Priority |
| -------- | --------------------------------------------- | ------------------------------------- | -------- |
| PRED-001 | Get congestion prediction for a valid road_id | 200 with predicted_level + confidence | High     |
| PRED-002 | Get peak-hour prediction                      | 200 with peak-hour window             | High     |
| PRED-003 | Get delay estimation for a road               | 200 with delay estimate in minutes    | High     |
| PRED-004 | Verify model_version field is present         | Field present and non-empty           | Medium   |
| PRED-005 | Verify confidence value range                 | Value between 0 and 1                 | Medium   |
| PRED-006 | Request prediction with invalid road_id       | 400/404 error returned                | Medium   |
| PRED-007 | Measure prediction endpoint response latency  | Response under agreed threshold (~2s) | Medium   |

## 3. Route Analysis (API + UI)

| Test ID        | Test Case                                                           | Expected Result                                     | Priority |
| -------------- | ------------------------------------------------------------------- | --------------------------------------------------- | -------- |
| ROUTE-001      | Request optimized route between valid origin/destination            | 200 with route path + ETA                           | High     |
| ROUTE-002      | Request alternate routes                                            | 200 with 2+ alternate options                       | High     |
| ROUTE-003      | Request travel-time estimation                                      | 200 with travel time in minutes                     | High     |
| ROUTE-004      | Request road conditions along a route                               | 200 with hazards/construction flags                 | Medium   |
| ROUTE-005      | Request route with invalid origin/destination                       | 400 validation error                                | Medium   |
| ROUTE-006      | Verify route response structure                                     | Segments, distance, ETA, congestion fields present  | High     |
| ROUTE-007 (UI) | Select origin & destination on Route Analysis page and run analysis | Route cards + map render with ETA/distance KPIs     | High     |
| ROUTE-008 (UI) | Switch optimization mode (AI Optimal / Fastest / Eco)               | Recommended route updates accordingly               | Medium   |
| ROUTE-009 (UI) | Use temporal forecast horizon control (0/15/30/60/120 min)          | Forecast cards and speed profile update per horizon | Medium   |

## 4. Maps Integration (UI)

| Test ID | Test Case                                       | Expected Result                                                       | Priority |
| ------- | ----------------------------------------------- | --------------------------------------------------------------------- | -------- |
| MAP-001 | Load Live Traffic map (`live maps.html`)        | Map renders with road markers/incidents                               | High     |
| MAP-002 | Load Route Analysis map (`route-analysis.html`) | Map renders selected route path                                       | High     |
| MAP-003 | Toggle map tile layer (OSM / Terrain)           | Tile layer switches correctly                                         | Low      |
| MAP-004 | Toggle congestion heatmap                       | Heatmap overlay shows/hides                                           | Medium   |
| MAP-005 | Click a road on the live map                    | Road detail modal opens with congestion/speed/density + AI prediction | High     |
| MAP-006 | Verify map reflects Route Analysis selection    | Route path and KPIs on map match selected route                       | Medium   |

## 5. Frontend (UI)

| Test ID   | Test Case                                                                  | Expected Result                                                | Priority |
| --------- | -------------------------------------------------------------------------- | -------------------------------------------------------------- | -------- |
| FE-M2-001 | Route Analysis page loads without console errors                           | Page renders, no blocking JS errors in DevTools console        | High     |
| FE-M2-002 | Prediction/forecast charts render (speed profile, temporal forecast cards) | Charts populated with data                                     | High     |
| FE-M2-003 | Travel-time display updates after route calculation                        | Correct ETA/travel time shown                                  | High     |
| FE-M2-004 | Road-condition display shows hazards/construction when present             | Panel visible with correct info                                | Medium   |
| FE-M2-005 | Prediction report download control works                                   | File download triggers without error                           | Medium   |
| FE-M2-006 | Loading state shown while route/prediction is calculating                  | Spinner/loading indicator visible                              | Low      |
| FE-M2-007 | Graceful behavior when backend is unreachable                              | Mock-fallback data or clear error message shown, no blank page | High     |

## 6. Regression (Milestone 1)

| Test ID | Test Case                                            | Expected Result                        | Priority |
| ------- | ---------------------------------------------------- | -------------------------------------- | -------- |
| REG-001 | Login with valid credentials                         | User logs in successfully              | High     |
| REG-002 | RBAC — operator vs admin vs public dashboard access  | Correct dashboard/permissions per role | High     |
| REG-003 | Live Traffic Monitoring page loads and displays data | Live feed populated                    | High     |

## 7. Integration

| Test ID | Test Case                                                                         | Expected Result                                 | Priority |
| ------- | --------------------------------------------------------------------------------- | ----------------------------------------------- | -------- |
| INT-001 | Full flow: Authentication → Live Traffic → Prediction → Route Analysis → Frontend | Each stage hands off data correctly to the next | High     |

---

**Total test cases authored:** 32
**Execution status and evidence:** see [milestone2_day2_test_execution_report.md](milestone2_day2_test_execution_report.md)

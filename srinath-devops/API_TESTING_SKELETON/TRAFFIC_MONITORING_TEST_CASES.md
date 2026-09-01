# TRAFFIC MONITORING TEST CASES

## Project
TrafficVision AI — Milestone 1

## Scope
Traffic ingestion, live monitoring, road-specific monitoring, density metrics and congestion-level calculation.

## Traffic Monitoring API Contracts

### Live Traffic
`GET /api/v1/traffic/live`

Expected response:
`200 [ { road_id, vehicle_count, density, congestion_level, updated_at } ]`

### Road-Specific Traffic
`GET /api/v1/traffic/road/{road_id}`

Expected response:
`200 { road_id, name, congestion_level, history[] }`

### Density
`GET /api/v1/traffic/density`

Expected response:
`200` with aggregated density metrics for dashboard KPIs.

## Test Cases

| Test ID | Test Case | Expected Result | Priority | Status |
|---|---|---|---|---|
| TRAF-001 | Request live traffic data | HTTP 200 and live traffic records returned | High | Not Run |
| TRAF-002 | Verify live record contains road_id | road_id is present | High | Not Run |
| TRAF-003 | Verify live record contains vehicle_count | vehicle_count is present and valid | High | Not Run |
| TRAF-004 | Verify live record contains density | density is present | High | Not Run |
| TRAF-005 | Verify live record contains congestion_level | congestion_level is present | High | Not Run |
| TRAF-006 | Verify live record contains updated_at | timestamp is present | Medium | Not Run |
| TRAF-007 | Request traffic for a valid road_id | HTTP 200 and road information returned | High | Not Run |
| TRAF-008 | Request traffic for an invalid/nonexistent road_id | Appropriate error response returned | Medium | Not Run |
| TRAF-009 | Verify road response contains history[] | History array is returned | Medium | Not Run |
| TRAF-010 | Request aggregated density metrics | HTTP 200 and density metrics returned | High | Not Run |
| TRAF-011 | Verify density calculation using available test data | Calculated density matches the implemented project rule | High | Not Run |
| TRAF-012 | Verify congestion level for low-density traffic | Congestion level follows the implemented threshold/rule | High | Not Run |
| TRAF-013 | Verify congestion level for high-density traffic | Congestion level follows the implemented threshold/rule | High | Not Run |
| TRAF-014 | Verify traffic data updates over time | New readings are reflected by the live endpoint | Medium | Not Run |
| TRAF-015 | Send invalid request parameters where applicable | Appropriate validation/error response returned | Medium | Not Run |

## Test Execution Note

The SRS requires congestion-level computation from live traffic data. Exact threshold values are not specified in the SRS, so expected congestion values should be based on the implementation agreed by the Data/Monitoring intern rather than invented in this test document.

All cases are initially marked `Not Run`.

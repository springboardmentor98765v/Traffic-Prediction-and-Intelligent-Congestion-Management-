# Milestone 2 — Day 6 Testing, Performance & QA

## 1. Objective

Validate the TrafficVision AI prediction and route-ranking services through
functional testing, error handling, edge-case testing, and response-time
measurement.

---

## 2. Services Tested

The following APIs were tested:

- `/api/v1/predict/congestion`
- `/api/v1/predict/peak-hours`
- `/api/v1/predict/delay`
- `/api/v1/routes/rank`

---

## 3. Functional API Testing

### Congestion Prediction

Endpoint:

```text
GET /api/v1/predict/congestion?road_id=R001
```

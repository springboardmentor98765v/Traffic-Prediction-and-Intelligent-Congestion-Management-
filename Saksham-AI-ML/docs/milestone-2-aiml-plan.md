# Milestone 2: AI/ML & Intelligent Routing Architecture Plan (Day 1)

## 1. Scope & Objectives
* **Owner**: Intern 3 (AI/ML & Intelligent Routing)
* **Goal**: Replace Milestone 1 heuristic baseline with a real trained machine learning pipeline:
  1. Real-time Congestion Classification (`LOW`, `MEDIUM`, `HIGH`, `SEVERE`).
  2. Peak-Hour Window Forecasting per road segment.
  3. Estimated Travel Delay (in minutes) per road segment.
  4. Congestion-Aware Route-Ranking logic for Route Analysis.
* **Target Latency**: ~1–2 seconds response SLA across all prediction endpoints.

---

## 2. Feature Engineering Requirements (Dependency for Intern 2)
Tabular features to extract from historical time-series data:

| Feature Name | Data Type | Description | Source / Derivation |
| :--- | :--- | :--- | :--- |
| `road_id` | String / Int | Identifier of the monitored road segment | Road Network Registry |
| `hour_of_day` | Integer (0–23) | Hour when observation was recorded | Timestamp decomposition |
| `day_of_week` | Integer (0–6) | Day index (Monday=0, Sunday=6) | Timestamp decomposition |
| `is_weekend` | Boolean / Int | 1 if Saturday or Sunday, else 0 | Derived flag |
| `is_rush_hour` | Boolean / Int | 1 if 08:00–11:00 or 17:00–20:00, else 0 | Domain window heuristic |
| `rolling_avg_density` | Float (0.0–1.0) | Moving average vehicle density over prior 15 mins | Historical rolling window |
| `rolling_avg_speed` | Float (km/h) | Moving average vehicle speed over prior 15 mins | Historical rolling window |
| `recent_vehicle_count`| Integer | Total vehicle count detected in current window | Upstream sensor aggregation |

---

## 3. Frozen API Contracts (Intern 3 Deliverables)

### 3.1 Real-Time Congestion Prediction
* **Route**: `GET /api/v1/predict/congestion`
* **Query Parameters**:
  * `road_id` (String, Required) - e.g., `1` or `R001`
  * `time` (ISO-8601 Timestamp String, Optional) - e.g., `2026-09-10T08:30:00`
* **Status**: `200 OK`
* **Response Body**:
```json
{
  "road_id": "1",
  "predicted_level": "MEDIUM",
  "confidence": 0.82,
  "model_version": "model-v1",
  "timestamp": "2026-09-10T08:30:00",
  "data_source": "trained-random-forest"
}
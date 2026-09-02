# Historical Data for ML Training

## 1. Purpose
This document defines the historical traffic data structure available for Milestone 2 feature engineering and ML model development.

The current dataset is synthetic/historical development data. It should not automatically be treated as verified real-world ground truth.

## 2. Current Data Flow
```text
Historical/Synthetic CSV
        ↓
Traffic Ingestion
        ↓
PostgreSQL traffic_readings
        ↓
Feature Engineering
        ↓
ML Training Dataset
```

Live prediction input:
```text
GET /api/v1/traffic/live
```

## 3. Historical Record Structure

| Field | Description | Suggested ML Use |
|---|---|---|
| `reading_id` | Unique reading identifier | Tracking |
| `road_id` | Road identifier | Road patterns |
| `sensor_id` | Sensor identifier | Sensor/road grouping |
| `reading_timestamp` | Reading date/time | Time-series features |
| `vehicle_count` | Number of vehicles | Traffic volume |
| `avg_speed_kmph` | Average speed | Traffic condition |
| `density_vehicles_per_km` | Vehicles per km | Congestion feature |
| `congestion_level` | Current heuristic class | Candidate target |

The deployed CSV/database schema is the source of truth if field names differ.

## 4. Example Record
```json
{
  "road_id": "R001",
  "sensor_id": "S001",
  "timestamp": "2026-08-26 22:00:00",
  "vehicle_count": 28,
  "avg_speed_kmph": 43.3,
  "density_vehicles_per_km": 5.6,
  "congestion_level": "Low"
}
```

## 5. Candidate Features
Traffic:
```text
vehicle_count
density_vehicles_per_km
avg_speed_kmph
```

Road:
```text
road_id
road_capacity
road_length_km
```

Time:
```text
hour_of_day
day_of_week
is_weekend
is_peak_hour
```

Historical/lag:
```text
previous_density
previous_vehicle_count
previous_speed
rolling_average_density
rolling_average_speed
density_change
speed_change
```

## 6. Candidate Target
Current congestion classes:
```text
Low
Medium
High
Severe
```

Before supervised training, the ML team should verify how these labels were generated and whether they are appropriate as ground truth.

## 7. Data Preparation
Before training:
1. Validate timestamps.
2. Check duplicates.
3. Check missing values.
4. Check negative vehicle counts.
5. Check negative speeds.
6. Check invalid density.
7. Validate road IDs.
8. Validate sensor IDs.
9. Inspect outliers.
10. Check class distribution.
11. Sort by road and timestamp.
12. Prevent future-data leakage.

## 8. Time-Series Split
Prefer chronological validation:
```text
Earlier data → Training
Later data   → Validation
Latest data  → Test
```

## 9. Leakage Prevention
When predicting time T, do not use measurements from future timestamps unless the prediction problem explicitly defines that future information as available.

## 10. Live API Input
```http
GET /api/v1/traffic/live
```

Current response:
```json
[
  {
    "road_id": "R001",
    "vehicle_count": 28,
    "density": 5.6,
    "congestion_level": "Low",
    "updated_at": "2026-08-26T22:00:00"
  }
]
```

For richer ML training, use historical records containing timestamp, sensor, speed, density, and traffic-volume fields.

## 11. Suggested Model-Ready Dataset
```text
timestamp
road_id
sensor_id
vehicle_count
avg_speed_kmph
density_vehicles_per_km
hour_of_day
day_of_week
is_weekend
is_peak_hour
lag/rolling features
target_congestion_level
```

## 12. Baseline vs ML
Milestone 1:
```text
Traffic Data → Heuristic Rules → Congestion Level
```

Milestone 2:
```text
Historical Data → Features → Trained ML Model → Predicted Congestion
```

The heuristic system can be retained as a baseline.

## 13. Evaluation
Recommended classification metrics:
```text
Accuracy
Precision
Recall
F1-score
Confusion Matrix
```

For imbalanced classes, review per-class precision, recall, and F1 rather than accuracy alone.

## 14. Handover
Intern 3 can consume:
```http
GET /api/v1/traffic/live
```

Current live fields:
```text
road_id
vehicle_count
density
updated_at
```

The existing `congestion_level` is a monitoring/heuristic result and should not automatically be treated as verified real-world ground truth.

## 15. Status
**Historical data structure documented for Milestone 2 ML planning.**

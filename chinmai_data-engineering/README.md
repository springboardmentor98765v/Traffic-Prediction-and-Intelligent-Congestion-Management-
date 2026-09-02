# Traffic Monitoring Service

## Overview
FastAPI-based Traffic Monitoring backend for Milestone 1. It provides traffic ingestion, PostgreSQL persistence, Redis caching, congestion tracking, monitoring APIs, Gateway integration, testing, and database optimization.

> **Scope:** Milestone 1 uses synthetic/historical traffic data and heuristic/rule-based congestion logic. A trained ML prediction model is planned for Milestone 2.

## Day 1–Day 7 Summary

### Day 1 – Data Preparation
- Prepared and reviewed the synthetic traffic monitoring dataset.
- Identified road, sensor, timestamp, vehicle count, speed, density, and congestion fields.

### Day 2 – PostgreSQL + Redis Ingestion
- Created PostgreSQL traffic storage.
- Implemented CSV-to-PostgreSQL ingestion.
- Added Redis caching for latest sensor readings.
- Verified PostgreSQL and Redis operation.

### Day 3 – Monitoring APIs
Implemented:
```text
GET /api/v1/traffic/live
GET /api/v1/traffic/road/{road_id}
GET /api/v1/traffic/density
```
Swagger:
```text
http://127.0.0.1:8000/docs
```

### Day 4 – Congestion Tracking + Redis
- Added congestion state/history handling.
- Added Redis-backed low-latency live reads.
- Prepared the live monitoring feed for the prediction service.

### Day 5 – API Gateway Integration
Gateway:
```text
http://127.0.0.1:8000
```
Traffic routes:
```text
/api/v1/traffic/live
/api/v1/traffic/road/{road_id}
/api/v1/traffic/density
```
Joint test:
```powershell
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/live
```
Expected:
```text
HTTP/1.1 200 OK
```

### Day 6 – Testing + DB Optimization
- Added congestion, ingestion, and API regression tests.
- **20/20 tests passed.**
- Used PostgreSQL `EXPLAIN ANALYZE`.
- Verified composite index:
```sql
CREATE INDEX idx_traffic_road_timestamp_reading
ON traffic_readings (road_id, reading_timestamp DESC, reading_id DESC);
```
- Observed road-specific query execution improvement from **8.650 ms to 0.552 ms (~93.6%)**.
- QA status: **No pending defects reported by QA.**

### Day 7 – Final Validation + Handover
- Final monitoring/API/Gateway validation completed.
- Module documentation completed.
- Historical-data documentation completed.
- Milestone 2 handover and improvement recommendations completed.
- Confirmed Milestone 1 is heuristic/rule-based, not a trained ML model.

## API Endpoints

### Live Traffic
```http
GET /api/v1/traffic/live
```
```text
http://127.0.0.1:8000/api/v1/traffic/live
```

Example:
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

### Road Traffic
```http
GET /api/v1/traffic/road/{road_id}
```

### Density
```http
GET /api/v1/traffic/density
```

## Configuration

PostgreSQL:
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=traffic_monitoring
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_LOCAL_POSTGRES_PASSWORD
```

Redis:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

Do not commit real credentials.

## Run

```powershell
pip install -r requirements.txt
python -m pytest -v
```

Run FastAPI from the directory containing `main.py`:
```powershell
python -m uvicorn main:app --reload --port 8000
```

Swagger:
```text
http://127.0.0.1:8000/docs
```

## Validation

```powershell
python -m pytest -v
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/live
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/road/R001
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/density
```

## Milestone 2 Handover

Primary live feed:
```http
GET /api/v1/traffic/live
```

Current live fields:
```text
road_id
vehicle_count
density
congestion_level
updated_at
```

Historical fields include:
```text
reading_id
road_id
sensor_id
reading_timestamp
vehicle_count
avg_speed_kmph
density_vehicles_per_km
congestion_level
```

Potential ML features:
```text
vehicle_count
density
avg_speed_kmph
hour_of_day
day_of_week
road_id
road_capacity
historical/lag features
```

Milestone 2 should integrate real sensor/API data, validate and normalize it, engineer features, train/evaluate an ML model, and expose predictions through the Gateway.

## Documentation
- `TRAFFIC_MONITORING_MODULE_DOCUMENTATION.md`
- `HISTORICAL_DATA_FOR_ML_TRAINING.md`
- `RECOMMENDED_MILESTONE_2_IMPROVEMENTS.md`

## Final Status
**Traffic Monitoring Module – Milestone 1: COMPLETED**

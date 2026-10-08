# Traffic Monitoring Module Documentation

## 1. Purpose

The Traffic Monitoring Module provides backend services for traffic ingestion, persistent storage, live monitoring, road-specific traffic access, density summaries, congestion tracking, Redis caching, Gateway integration, testing, and database optimization.

## 2. Milestone 1 Scope

Milestone 1 establishes the monitoring foundation using synthetic/historical data and heuristic/rule-based congestion logic.

It does **not** contain a trained AI/ML prediction model.

## 3. Technology Stack

| Layer           | Technology     |
| --------------- | -------------- |
| Backend         | Python         |
| API             | FastAPI        |
| Server          | Uvicorn        |
| Database        | PostgreSQL     |
| Cache           | Redis          |
| Testing         | pytest         |
| Data processing | Pandas / NumPy |
| Version control | Git / GitHub   |

## 4. Architecture

```text
Synthetic/Historical CSV
        ↓
Traffic Ingestion
        ↓
 PostgreSQL ←→ Redis
        ↓
Traffic Monitoring APIs
        ↓
API Gateway
        ↓
Prediction Service / Dashboard
```

## 5. Data Storage

PostgreSQL database:

```text
traffic_monitoring
```

Main traffic table:

```text
traffic_readings
```

Relevant traffic fields:

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

## 6. Redis

Redis stores latest readings for fast access.

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

Example key:

```text
traffic:sensor:S001
```

Example value:

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

## 7. APIs

### GET /api/v1/traffic/live

Returns latest traffic information.

```powershell
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/live
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

### GET /api/v1/traffic/road/{road_id}

Returns traffic information for a specific road.

```powershell
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/road/R001
```

Unknown roads return `404 Not Found`.

### GET /api/v1/traffic/density

Returns density summary.

Example:

```json
{
  "total_roads": 6,
  "average_density": 6.62,
  "maximum_density": 11.33,
  "minimum_density": 0.22,
  "high_congestion_roads": 0,
  "severe_congestion_roads": 0
}
```

## 8. Congestion Logic

Milestone 1 uses heuristic/rule-based congestion classification. Automated tests cover Low, Medium, High, Severe, boundary conditions, and invalid capacity.

The exact thresholds in source code are authoritative.

## 9. Congestion Tracking

Historical readings allow the service/team to analyze:

- congestion changes over time
- density trends
- vehicle-count trends
- speed trends
- road utilization
- future prediction features

## 10. Database Optimization

Composite index:

```sql
CREATE INDEX idx_traffic_road_timestamp_reading
ON traffic_readings
(road_id, reading_timestamp DESC, reading_id DESC);
```

Validated using:

```sql
EXPLAIN ANALYZE
```

Observed:

```text
Before: 8.650 ms
After:  0.552 ms
Improvement: approximately 93.6%
```

The optimized execution plan used:

```text
idx_traffic_road_timestamp_reading
```

## 11. Automated Testing

Run:

```powershell
python -m pytest -v
```

Day 6 result:

```text
20 passed
```

Coverage includes congestion logic, ingestion validation, CSV validation, live API, density API, and unknown-road handling.

## 12. Gateway Integration

Gateway:

```text
http://127.0.0.1:8000
```

Traffic routes:

```text
GET /api/v1/traffic/live
GET /api/v1/traffic/road/{road_id}
GET /api/v1/traffic/density
```

Joint test:

```powershell
curl.exe -i http://127.0.0.1:8000/api/v1/traffic/live
```

Expected:

```text
HTTP/1.1 200 OK
```

## 13. Milestone 2 Contract

Prediction service can consume:

```http
GET /api/v1/traffic/live
```

Current fields:

```text
road_id
vehicle_count
density
congestion_level
updated_at
```

Historical training structure is documented separately in:

```text
HISTORICAL_DATA_FOR_ML_TRAINING.md
```

## 14. Known Limitations

- Current data is synthetic/historical.
- Congestion is heuristic/rule-based.
- No trained ML model is included.
- Local development uses localhost services.
- Real sensor/API mappings are still to be finalized.

## 15. Final Status

**Traffic Monitoring Module – Milestone 1: COMPLETE**

Ready for Milestone 1 demonstration and Milestone 2 handover.

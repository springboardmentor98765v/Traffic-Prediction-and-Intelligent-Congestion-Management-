# Traffic-Prediction-and-Intelligent-Congestion-Management-
TrafficVision AI — An AI-powered smart traffic prediction and congestion management platform for real-time monitoring, congestion forecasting, route optimization, traffic analytics, and intelligent alerts.
# TrafficVision AI — Traffic Monitoring Module
**Owner:** Intern 2 — Data Engineering & Traffic Monitoring
**Status:** Milestone 1 — Complete, Signed Off Day 7

---

## 1. Overview

This module is responsible for everything related to traffic data in TrafficVision AI:
- Storing traffic data in a structured database schema
- Simulating a live traffic feed (standing in for real sensors, which don't exist yet)
- Exposing that data through a REST API
- Caching for performance, and tracking congestion state over time
- Being reachable through a shared API Gateway

---

## 2. Architecture

```
[ingest_live_data.py]  --writes-->  [PostgreSQL: trafficvision DB]
                                              |
                                              v
                                    [main.py: FastAPI Service]
                                     (checks Redis cache first)
                                              |
                                              v
                                        [Redis Cache]
                                              |
                                              v
                                   [gateway.py: API Gateway]
                                              |
                                              v
                                    (Frontend / other consumers)
```

---

## 3. Files in This Module

| File | Purpose |
|---|---|
| `schema.sql` | Database schema: `roads`, `sensors`, `traffic_readings` tables + `latest_traffic_status` view |
| `generate_data.py` | One-time synthetic dataset generator (Day 1) |
| `congestion_logic.py` | Reusable density → congestion-level threshold function |
| `ingest_live_data.py` | Continuous live data simulator — writes a new reading per road every 5 seconds |
| `congestion_tracking.py` | Road utilization % calculation + congestion state-history grouping |
| `redis_cache.py` | Redis get/set wrapper with graceful fallback if Redis is unavailable |
| `main.py` | The Traffic Monitoring Service — all 4 REST API endpoints |
| `gateway.py` | Minimal API Gateway demo — proxies requests to `main.py` |
| `test_congestion_logic.py` | Unit tests for the congestion threshold rule |
| `test_congestion_tracking.py` | Unit tests for utilization + state history |
| `query_optimization_checks.sql` | EXPLAIN ANALYZE checks + covering index |
| `final_smoke_test.py` | End-to-end validation script (Day 7) |

---

## 4. Setup Instructions (From Scratch)

```bash
# 1. Install PostgreSQL and Redis (via Docker), plus Python packages
pip install fastapi uvicorn psycopg2-binary redis httpx requests pytest

# 2. Create the database
psql -U postgres -c "CREATE DATABASE trafficvision;"

# 3. Load the schema
psql -U postgres -d trafficvision -f schema.sql

# 4. Insert sample roads + sensors
psql -U postgres -d trafficvision -c "INSERT INTO roads (road_name, area, road_type, length_km, lanes) VALUES ('Anna Salai','Chennai Central','arterial',6.5,4), ('OMR','Sholinganallur','highway',12.0,6), ('Mount Road','T. Nagar','arterial',4.2,4), ('GST Road','Tambaram','highway',15.0,6), ('Velachery Main Road','Velachery','local',3.1,2);"
psql -U postgres -d trafficvision -c "INSERT INTO sensors (road_id, sensor_type, is_active) SELECT road_id, 'camera', TRUE FROM roads;"

# 5. Start Redis (via Docker)
docker run -d -p 6379:6379 redis

# 6. Edit DB_CONFIG password in ingest_live_data.py and main.py

# 7. Run everything (3 terminals)
python ingest_live_data.py
uvicorn main:app --reload
uvicorn gateway:app --reload --port 9000

# 8. Validate everything works
python final_smoke_test.py
```

---

## 5. API Reference

### `GET /api/v1/traffic/live`
Returns the most recent reading for every road. Cached in Redis for 5 seconds.
```json
[{"road_id": 1, "vehicle_count": 489, "density": 25.85, "congestion_level": "LOW", "updated_at": "..."}]
```

### `GET /api/v1/traffic/road/{road_id}`
Returns details + recent history for one road. Returns 404 if the road doesn't exist.
```json
{"road_id": 1, "name": "Anna Salai", "congestion_level": "LOW", "history": [...]}
```

### `GET /api/v1/traffic/road/{road_id}/tracking`
Returns current road utilization % and grouped congestion state history.
```json
{"road_id": 1, "name": "Anna Salai", "current_utilization_percent": 45.5, "congestion_state_history": [...]}
```

### `GET /api/v1/traffic/density`
Returns city-wide aggregated stats.
```json
{"avg_density": 52.3, "total_roads_monitored": 5, "low_count": 1, "moderate_count": 2, "high_count": 1, "severe_count": 1}
```

---

## 6. Testing

```bash
pytest test_congestion_logic.py test_congestion_tracking.py -v   # 21 unit tests
python final_smoke_test.py                                       # end-to-end validation
```

---

## 7. Known Limitations (Milestone 1 Scope)

- All traffic data is **synthetic** — generated by a script, not real sensors
- No real weather, incident, or road-interaction effects modeled
- The Gateway (`gateway.py`) is a minimal demo version — the real Gateway (owned by Intern 1) will also route Auth and Prediction services
- Congestion thresholds are simple fixed rules, not learned from real data — see `M2_Historical_Data_Feed_Documentation.md` for full detail on this handed off to the AI/ML intern

---

## 8. Milestone 1 Sign-Off

All Day 1–7 checklist items for this module are complete:
- [x] Schema designed and deployed
- [x] Live data ingestion pipeline running
- [x] REST API built matching the frozen interface contract
- [x] Redis caching + congestion tracking implemented
- [x] Integrated and verified behind an API Gateway
- [x] Unit tests written and passing (21/21)
- [x] Query performance checked and optimized
- [x] Final end-to-end smoke test passing
- [x] No deployment activity performed (explicitly out of scope for Milestone 1)

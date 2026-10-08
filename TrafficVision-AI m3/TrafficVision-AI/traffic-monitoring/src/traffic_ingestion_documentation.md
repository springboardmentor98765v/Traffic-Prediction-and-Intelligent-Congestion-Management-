# Traffic Ingestion Module Documentation

## Overview

The Traffic Ingestion module is responsible for loading synthetic traffic data into the system's persistent storage (PostgreSQL) and maintaining a real-time cache (Redis) of the latest traffic readings. This module forms the foundation of the TrafficVision-AI data pipeline by continuously feeding traffic observations that are later consumed by the Traffic Monitoring API and AI Engine services.

## Architecture Context

As described in the TrafficVision-AI Milestone 1 documentation:

```
SYNTHETIC TRAFFIC DATASET
          ↓
Traffic Ingestion
          ↓
     PostgreSQL
          ↓
      Redis Cache
          ↓
Traffic Monitoring API
     /api/v1/traffic/live
          ↓
       AI Engine
          ↓
Heuristic Prediction
```

This module implements the "Traffic Ingestion" step in the data flow, positioned between the synthetic dataset and the PostgreSQL/Redis storage layers.

## Key Responsibilities

1. **Data Loading**: Reads traffic observations from a CSV file containing synthetic traffic data
2. **Congestion Calculation**: Determines congestion levels using vehicle count and road capacity
3. **Persistent Storage**: Inserts each traffic reading into PostgreSQL for historical analysis
4. **Real-time Caching**: Maintains latest traffic readings in Redis with 30-second TTL for low-latency API access
5. **Cache Management**: Clears live traffic cache after each insert to ensure frontend receives updated data

## File Location

`traffic-monitoring/src/traffic_ingestion.py`

## Dependencies

- **PostgreSQL**: Primary storage for traffic readings (via psycopg2)
- **Redis**: Cache layer for latest traffic data
- **Internal Modules**:
  - `congestion_calculator`: Provides `calculate_congestion()` function
  - `redis_cache`: Handles Redis operations (`cache_latest_reading`, `get_redis_client`, `clear_live_traffic_cache`)
- **Environment**: Loads configuration via python-dotenv

## Configuration (Environment Variables)

| Variable                  | Description                  | Default              |
| ------------------------- | ---------------------------- | -------------------- |
| `POSTGRES_HOST`           | Database host                | `localhost`          |
| `POSTGRES_PORT`           | Database port                | `5432`               |
| `POSTGRES_DB`             | Database name                | `traffic_monitoring` |
| `POSTGRES_USER`           | Database user                | `postgres`           |
| `POSTGRES_PASSWORD`       | Database password            | _(required)_         |
| `INGEST_INTERVAL_SECONDS` | Delay between record inserts | `5`                  |

## Data Flow

1. **Initialization**: Loads environment variables and establishes connections to PostgreSQL and Redis
2. **CSV Processing**: Reads the synthetic traffic dataset row-by-row
3. **Per-Record Processing**:
   - Calculates congestion level using vehicle count and road capacity
   - Prepares values for database insertion
   - Inserts record into `traffic_readings` table
   - Commits transaction to PostgreSQL
   - Caches the latest reading in Redis
   - Clears the live traffic cache to trigger cache refresh
   - Logs processing progress
   - Waits for configured interval before next record
4. **Termination**: Closes database and Redis connections

## Database Schema Interaction

Inserts data into the `traffic_readings` table with these columns:

- `road_id` (string)
- `sensor_id` (string)
- `reading_timestamp` (string/timestamp)
- `vehicle_count` (integer)
- `avg_speed_kmph` (float)
- `road_capacity` (integer)
- `traffic_density_vehicles_per_km` (float)
- `congestion_level` (string: Low/Medium/High)
- `latitude` (float)
- `longitude` (float)

## Redis Cache Structure

Each cached reading contains:

```json
{
  "road_id": "string",
  "sensor_id": "string",
  "timestamp": "string",
  "vehicle_count": "integer",
  "avg_speed_kmph": "float",
  "density_vehicles_per_km": "float",
  "congestion_level": "string"
}
```

The cache key is managed internally by the `redis_cache` module with a 30-second TTL.

## Congestion Calculation

Uses the heuristic from `congestion_calculator.calculate_congestion()`:

- Density < 10 vehicles/km → "Low"
- 10 ≤ Density < 20 vehicles/km → "Medium"
- Density ≥ 20 vehicles/km → "High"

Where density = vehicle_count / road_capacity * 1000 (assuming road_capacity is in vehicles/km)

## Usage

Run as a standalone script:

```bash
cd traffic-monitoring/src
python traffic_ingestion.py
```

Or import and call the `ingest()` function:

```python
from traffic_ingestion import ingest
ingest(max_records=100)  # Optional limit for testing
```

## Important Notes

1. **Synthetic Data**: Uses a predefined CSV dataset - not real-time sensor data
2. **Continuous Operation**: Designed to run continuously, inserting records at configured intervals
3. **Error Handling**: Uses try/finally to ensure database connections are properly closed
4. **Atomic Operations**: Each insert is committed immediately to PostgreSQL
5. **Cache Consistency**: Live traffic cache is cleared after each insert to ensure API consumers get fresh data

## Integration Points

- **Consumed by**: Traffic Monitoring API (via PostgreSQL direct queries and Redis cache)
- **Provides data to**: AI Engine (via Traffic Monitoring API)
- **Depends on**: PostgreSQL (persistent storage), Redis (caching layer)

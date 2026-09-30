# M3 Day 5 - Historical Reports and Analytics Query Optimization

## Objective

Build a downloadable historical traffic report endpoint and improve Analytics query performance without changing existing M1/M2 behavior.

## 1. Historical Report API

Endpoint:

`GET /analytics/reports`

Optional parameters:

- `road_id`
- `start_date`
- `end_date`
- `limit` (1-50000, default 10000)

Example:

`GET /analytics/reports?road_id=R001&start_date=2026-07-27&end_date=2026-08-23`

The endpoint returns a CSV attachment containing historical traffic data.

CSV columns:

- road_id
- sensor_id
- reading_timestamp
- vehicle_count
- avg_speed_kmph
- road_capacity
- traffic_density_vehicles_per_km
- congestion_level
- latitude
- longitude
- source

The response also includes `X-Report-Row-Count`.

## 2. Query Optimization

Added `sql/m3_day5_analytics_optimization.sql`.

The optimization adds/ensures:

- Road + timestamp index
- Timestamp index
- Covering index for historical report queries

The covering index includes the report columns so PostgreSQL can reduce table lookups when the query plan permits an index-only scan.

## 3. Redis Analytics Cache

Added `src/analytics_cache.py`.

Trend and heatmap responses are cached using parameter-based Redis keys.

Default TTL:

`60 seconds`

Environment variables:

```env
ANALYTICS_CACHE_ENABLED=true
ANALYTICS_CACHE_TTL_SECONDS=60
```

If Redis is unavailable, the Analytics endpoints continue to use PostgreSQL instead of failing.

## 4. Performance Verification

Use:

`tests/m3_day5_performance.sql`

with PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` to verify actual execution time and index usage.

Do not claim a performance number until the SQL has been executed against the current database.

## 5. Regression Safety

M3 Day 5 is additive. Existing M1/M2 traffic, history, aggregation, road-condition, trend and heatmap functionality is retained.

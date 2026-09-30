-- ============================================================
-- M2 DAY 5 - PERFORMANCE VERIFICATION
-- ============================================================


-- ------------------------------------------------------------
-- HOURLY AGGREGATED LOOKUP
-- ------------------------------------------------------------

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    metric_timestamp,
    avg_vehicle_count,
    avg_speed_kmph,
    avg_density
FROM hourly_traffic_metrics
WHERE road_id = 'R001'
ORDER BY metric_timestamp DESC
LIMIT 24;


-- ------------------------------------------------------------
-- DAILY AGGREGATED LOOKUP
-- ------------------------------------------------------------

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    metric_date,
    avg_vehicle_count,
    avg_speed_kmph,
    avg_density
FROM daily_traffic_metrics
WHERE road_id = 'R001'
ORDER BY metric_date DESC
LIMIT 7;


-- ------------------------------------------------------------
-- HISTORICAL ROAD LOOKUP
-- ------------------------------------------------------------

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    reading_timestamp,
    vehicle_count,
    avg_speed_kmph,
    traffic_density_vehicles_per_km,
    congestion_level
FROM traffic_history
WHERE road_id = 'R001'
ORDER BY reading_timestamp DESC
LIMIT 24;
-- Run in PostgreSQL to verify the query plans used by M3 Day 5.
-- Replace dates/road_id as needed.

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    sensor_id,
    reading_timestamp,
    vehicle_count,
    avg_speed_kmph,
    road_capacity,
    traffic_density_vehicles_per_km,
    congestion_level,
    latitude,
    longitude,
    source
FROM traffic_history
WHERE road_id = 'R001'
  AND reading_timestamp >= '2026-07-27'
  AND reading_timestamp < '2026-08-24'
ORDER BY reading_timestamp ASC, history_id ASC
LIMIT 10000;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    road_id,
    EXTRACT(HOUR FROM (reading_timestamp AT TIME ZONE 'Asia/Kolkata'))::integer AS hour_of_day,
    AVG(vehicle_count),
    AVG(avg_speed_kmph),
    AVG(traffic_density_vehicles_per_km),
    COUNT(*)
FROM traffic_history
WHERE reading_timestamp >= '2026-07-27'
  AND reading_timestamp < '2026-08-24'
GROUP BY road_id, hour_of_day
ORDER BY road_id, hour_of_day;

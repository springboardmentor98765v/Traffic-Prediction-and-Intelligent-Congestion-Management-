-- Day 6: database query optimization
-- The live and density APIs use DISTINCT ON (road_id) and then
-- order by reading_timestamp DESC, reading_id DESC.
-- The road-history API filters by road_id and orders by the same keys.

CREATE INDEX IF NOT EXISTS idx_traffic_readings_road_latest
ON traffic_readings (road_id, reading_timestamp DESC, reading_id DESC)
INCLUDE (
    vehicle_count,
    traffic_density_vehicles_per_km,
    congestion_level,
    avg_speed_kmph
);

-- Sensor-level latest-reading queries.
CREATE INDEX IF NOT EXISTS idx_traffic_readings_sensor_latest
ON traffic_readings (sensor_id, reading_timestamp DESC, reading_id DESC)
INCLUDE (
    vehicle_count,
    traffic_density_vehicles_per_km,
    congestion_level,
    avg_speed_kmph
);

-- Keep the existing Day 5 indexes. The new indexes above are specifically
-- aligned with the ORDER BY clauses used by the monitoring service.

-- M3 DAY 5 - Analytics query optimization
-- Supports historical reports, trends and heatmap queries.

-- 1. Covering index for historical report queries.
CREATE INDEX IF NOT EXISTS idx_traffic_history_report
ON traffic_history (road_id, reading_timestamp ASC, history_id ASC)
INCLUDE (
    sensor_id,
    vehicle_count,
    avg_speed_kmph,
    road_capacity,
    traffic_density_vehicles_per_km,
    congestion_level,
    latitude,
    longitude,
    source
);

-- 2. General time-series scan support for date-range analytics.
CREATE INDEX IF NOT EXISTS idx_traffic_history_timestamp
ON traffic_history (reading_timestamp DESC);

-- 3. Road + timestamp support for trend/report filtering.
CREATE INDEX IF NOT EXISTS idx_traffic_history_road_time
ON traffic_history (road_id, reading_timestamp DESC);

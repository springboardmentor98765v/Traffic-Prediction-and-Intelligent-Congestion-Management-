-- M2 Day 2: indexed PostgreSQL time-series storage.
-- Run database/schema.sql first so roads exists.
\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS traffic_history (
    history_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL REFERENCES roads(road_id),
    sensor_id VARCHAR(20) NOT NULL,
    reading_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    vehicle_count INTEGER NOT NULL CHECK (vehicle_count >= 0),
    avg_speed_kmph NUMERIC(6,2) CHECK (avg_speed_kmph >= 0),
    road_capacity INTEGER NOT NULL CHECK (road_capacity > 0),
    traffic_density_vehicles_per_km NUMERIC(10,2) NOT NULL CHECK (traffic_density_vehicles_per_km >= 0),
    congestion_level VARCHAR(20) NOT NULL CHECK (congestion_level IN ('Low','Medium','High','Severe')),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    source VARCHAR(100) NOT NULL DEFAULT 'simulated_m2_day2',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_traffic_history_road_time
    ON traffic_history (road_id, reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_history_sensor_time
    ON traffic_history (sensor_id, reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_history_congestion_time
    ON traffic_history (road_id, congestion_level, reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_traffic_history_latest
    ON traffic_history (road_id, reading_timestamp DESC, history_id DESC)
    INCLUDE (vehicle_count, traffic_density_vehicles_per_km, congestion_level, avg_speed_kmph);

COMMIT;

-- Verification
SELECT current_database() AS database_name;
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'traffic_history'
ORDER BY ordinal_position;

SELECT indexname
FROM pg_indexes
WHERE tablename = 'traffic_history'
ORDER BY indexname;

-- ============================================================
-- Milestone 2 schema
-- Approved by Intern 1: same PostgreSQL DB, road_id FK,
-- TIMESTAMP WITH TIME ZONE, lowercase snake_case.
-- ============================================================

CREATE TABLE IF NOT EXISTS traffic_history (
    history_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL,
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
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_traffic_history_road FOREIGN KEY (road_id) REFERENCES roads(road_id)
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

CREATE TABLE IF NOT EXISTS road_conditions (
    condition_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL,
    condition_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    road_condition VARCHAR(50) NOT NULL,
    road_status VARCHAR(30) NOT NULL,
    incident_type VARCHAR(50),
    description TEXT,
    source VARCHAR(100) NOT NULL DEFAULT 'manual_or_external',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_road_conditions_road FOREIGN KEY (road_id) REFERENCES roads(road_id)
);

CREATE INDEX IF NOT EXISTS idx_road_conditions_road_time
    ON road_conditions (road_id, condition_timestamp DESC);

CREATE TABLE IF NOT EXISTS hourly_traffic_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL,
    metric_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    avg_vehicle_count NUMERIC(12,2),
    max_vehicle_count INTEGER,
    avg_speed_kmph NUMERIC(8,2),
    min_speed_kmph NUMERIC(8,2),
    avg_density NUMERIC(12,2),
    max_density NUMERIC(12,2),
    total_readings INTEGER NOT NULL DEFAULT 0,
    high_congestion_count INTEGER NOT NULL DEFAULT 0,
    severe_congestion_count INTEGER NOT NULL DEFAULT 0,
    high_congestion_percentage NUMERIC(6,2),
    severe_congestion_percentage NUMERIC(6,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_hourly_traffic_metrics UNIQUE (road_id, metric_timestamp),
    CONSTRAINT fk_hourly_metrics_road FOREIGN KEY (road_id) REFERENCES roads(road_id)
);

CREATE INDEX IF NOT EXISTS idx_hourly_metrics_road_time
    ON hourly_traffic_metrics (road_id, metric_timestamp DESC);

CREATE TABLE IF NOT EXISTS daily_traffic_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL,
    metric_date DATE NOT NULL,
    avg_vehicle_count NUMERIC(12,2),
    max_vehicle_count INTEGER,
    avg_speed_kmph NUMERIC(8,2),
    min_speed_kmph NUMERIC(8,2),
    avg_density NUMERIC(12,2),
    max_density NUMERIC(12,2),
    total_readings INTEGER NOT NULL DEFAULT 0,
    high_congestion_count INTEGER NOT NULL DEFAULT 0,
    severe_congestion_count INTEGER NOT NULL DEFAULT 0,
    high_congestion_percentage NUMERIC(6,2),
    severe_congestion_percentage NUMERIC(6,2),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_daily_traffic_metrics UNIQUE (road_id, metric_date),
    CONSTRAINT fk_daily_metrics_road FOREIGN KEY (road_id) REFERENCES roads(road_id)
);

CREATE INDEX IF NOT EXISTS idx_daily_metrics_road_date
    ON daily_traffic_metrics (road_id, metric_date DESC);

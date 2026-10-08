CREATE TABLE IF NOT EXISTS roads (
    road_id VARCHAR(20) PRIMARY KEY,
    road_name VARCHAR(150) NOT NULL,
    road_capacity INTEGER NOT NULL CHECK (road_capacity > 0),
    road_length_km NUMERIC(8,2) NOT NULL CHECK (road_length_km > 0),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6)
);

CREATE TABLE IF NOT EXISTS traffic_readings (
    reading_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL REFERENCES roads(road_id),
    sensor_id VARCHAR(20) NOT NULL,
    reading_timestamp TIMESTAMP NOT NULL,
    vehicle_count INTEGER NOT NULL CHECK (vehicle_count >= 0),
    avg_speed_kmph NUMERIC(6,2) CHECK (avg_speed_kmph >= 0),
    road_capacity INTEGER NOT NULL CHECK (road_capacity > 0),
    traffic_density_vehicles_per_km NUMERIC(10,2) NOT NULL CHECK (traffic_density_vehicles_per_km >= 0),
    congestion_level VARCHAR(20) NOT NULL
        CHECK (congestion_level IN ('Low', 'Medium', 'High', 'Severe')),
    latitude NUMERIC(10,6),
    longitude NUMERIC(10,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_traffic_sensor_time
ON traffic_readings(sensor_id, reading_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_traffic_road_time
ON traffic_readings(road_id, reading_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_traffic_road_congestion_time
ON traffic_readings(road_id, congestion_level, reading_timestamp DESC);
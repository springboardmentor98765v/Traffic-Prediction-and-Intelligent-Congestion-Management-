-- =========================================
-- TRAFFIC CONGESTION DATABASE SCHEMA
-- =========================================

-- 1. ROADS
CREATE TABLE IF NOT EXISTS roads (
    road_id SERIAL PRIMARY KEY,
    road_code VARCHAR(20) UNIQUE NOT NULL,
    road_name VARCHAR(100),
    road_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 2. SENSORS
CREATE TABLE IF NOT EXISTS sensors (
    sensor_id SERIAL PRIMARY KEY,
    road_id INTEGER NOT NULL,
    sensor_code VARCHAR(20) UNIQUE NOT NULL,
    sensor_name VARCHAR(100),
    sensor_type VARCHAR(30),
    location VARCHAR(255),
    status VARCHAR(20),
    installed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sensor_road
        FOREIGN KEY (road_id)
        REFERENCES roads(road_id)
);


-- 3. ROAD CAPACITY
CREATE TABLE IF NOT EXISTS road_capacity (
    capacity_id SERIAL PRIMARY KEY,
    road_id INTEGER NOT NULL,
    vehicle_capacity INTEGER NOT NULL,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_capacity_road
        FOREIGN KEY (road_id)
        REFERENCES roads(road_id),

    CONSTRAINT chk_vehicle_capacity
        CHECK (vehicle_capacity > 0),

    CONSTRAINT chk_capacity_dates
        CHECK (
            effective_to IS NULL
            OR effective_to > effective_from
        )
);


-- 4. TRAFFIC READINGS
CREATE TABLE IF NOT EXISTS traffic_readings (
    reading_id BIGSERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL,
    source_record_id BIGINT UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    vehicle_count INTEGER NOT NULL,
    density DECIMAL(5,2),
    congestion_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reading_sensor
        FOREIGN KEY (sensor_id)
        REFERENCES sensors(sensor_id),

    CONSTRAINT chk_vehicle_count
        CHECK (vehicle_count >= 0),

    CONSTRAINT chk_density
        CHECK (
            density IS NULL
            OR (density >= 0 AND density <= 1)
        ),

    CONSTRAINT chk_congestion_level
        CHECK (
            congestion_level IS NULL
            OR congestion_level IN
            ('LOW', 'MEDIUM', 'HIGH', 'SEVERE')
        )
);


-- 5. CONGESTION HISTORY
CREATE TABLE IF NOT EXISTS congestion_history (
    history_id BIGSERIAL PRIMARY KEY,
    road_id INTEGER NOT NULL,
    congestion_level VARCHAR(20) NOT NULL,
    density DECIMAL(5,2) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_history_road
        FOREIGN KEY (road_id)
        REFERENCES roads(road_id),

    CONSTRAINT chk_history_density
        CHECK (density >= 0 AND density <= 1),

    CONSTRAINT chk_history_level
        CHECK (
            congestion_level IN
            ('LOW', 'MEDIUM', 'HIGH', 'SEVERE')
        )
);


-- =========================================
-- 6. TRAFFIC STAGING
-- Raw CSV data landing table
-- =========================================

CREATE TABLE IF NOT EXISTS traffic_staging (
    staging_id BIGSERIAL PRIMARY KEY,

    reading_id BIGINT,
    source_record_id BIGINT,

    road_id INTEGER,
    road_code VARCHAR(20),
    road_name VARCHAR(100),
    road_description TEXT,

    sensor_id INTEGER,
    sensor_code VARCHAR(20),
    sensor_name VARCHAR(100),
    sensor_type VARCHAR(30),
    location VARCHAR(255),
    status VARCHAR(20),

    timestamp TIMESTAMP,
    vehicle_count INTEGER,
    vehicle_capacity INTEGER,
    density DECIMAL(5,2),
    congestion_level VARCHAR(20),
    previous_congestion_level VARCHAR(20),
    congestion_changed BOOLEAN,

    effective_from TIMESTAMP,
    effective_to TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================
-- INDEXES
-- =========================================

CREATE INDEX IF NOT EXISTS idx_traffic_timestamp
ON traffic_readings(timestamp);

CREATE INDEX IF NOT EXISTS idx_traffic_sensor_timestamp
ON traffic_readings(sensor_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_history_recorded_at
ON congestion_history(recorded_at);

CREATE INDEX IF NOT EXISTS idx_history_road_recorded
ON congestion_history(road_id, recorded_at);

-- Staging indexes
CREATE INDEX IF NOT EXISTS idx_staging_source_record
ON traffic_staging(source_record_id);

CREATE INDEX IF NOT EXISTS idx_staging_timestamp
ON traffic_staging(timestamp);

CREATE INDEX IF NOT EXISTS idx_staging_road
ON traffic_staging(road_id);

-- Road capacity index
CREATE INDEX IF NOT EXISTS idx_road_capacity_road
ON road_capacity(road_id);


-- =========================================
-- 7. ROAD CONDITIONS
-- =========================================

CREATE TABLE IF NOT EXISTS road_conditions (
    condition_id BIGSERIAL PRIMARY KEY,
    road_id INTEGER NOT NULL,
    condition_status VARCHAR(30) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_condition_road
        FOREIGN KEY (road_id)
        REFERENCES roads(road_id),

    CONSTRAINT chk_condition_status
        CHECK (
            condition_status IN
            ('OPEN', 'CONSTRUCTION', 'CLOSED')
        ),

    CONSTRAINT chk_condition_dates
        CHECK (
            end_time IS NULL
            OR end_time > start_time
        )
);

CREATE INDEX IF NOT EXISTS idx_road_conditions_road
ON road_conditions(road_id);

CREATE INDEX IF NOT EXISTS idx_road_conditions_time
ON road_conditions(start_time, end_time);
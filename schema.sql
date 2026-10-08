-- =====================================================
-- TrafficVision AI — Traffic Data Schema (Day 1)
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- DB: PostgreSQL
-- =====================================================

-- 1. ROADS: master list of road segments being monitored
CREATE TABLE roads (
    road_id         SERIAL PRIMARY KEY,
    road_name       VARCHAR(150) NOT NULL,
    area            VARCHAR(100),           -- e.g. "Anna Nagar", "OMR"
    road_type       VARCHAR(50),            -- e.g. "arterial", "highway", "local"
    length_km       NUMERIC(5,2),
    lanes           INT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 2. SENSORS: each road can have one or more sensors/cameras
CREATE TABLE sensors (
    sensor_id       SERIAL PRIMARY KEY,
    road_id         INT NOT NULL REFERENCES roads(road_id) ON DELETE CASCADE,
    sensor_type     VARCHAR(50) DEFAULT 'camera',  -- camera / inductive_loop / gps
    is_active       BOOLEAN DEFAULT TRUE,
    installed_at    TIMESTAMP DEFAULT NOW()
);

-- 3. TRAFFIC_READINGS: the live/historical time-series data
--    This is the table your ingestion script writes to every few seconds
CREATE TABLE traffic_readings (
    reading_id        BIGSERIAL PRIMARY KEY,
    road_id           INT NOT NULL REFERENCES roads(road_id) ON DELETE CASCADE,
    sensor_id         INT REFERENCES sensors(sensor_id),
    vehicle_count     INT NOT NULL,          -- number of vehicles detected in interval
    avg_speed_kmph    NUMERIC(5,2),          -- optional, useful signal for congestion
    density           NUMERIC(5,2) NOT NULL, -- vehicles per km (or normalized 0-1)
    congestion_level  VARCHAR(20) NOT NULL,  -- LOW / MODERATE / HIGH / SEVERE
    recorded_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for fast "latest reading per road" and time-range queries
CREATE INDEX idx_traffic_road_time ON traffic_readings (road_id, recorded_at DESC);

-- 4. (Optional but recommended) CONGESTION_HISTORY view
--    Useful later for Intern 3 (feature engineering) and Day 4 history tracking
CREATE VIEW latest_traffic_status AS
SELECT DISTINCT ON (road_id)
    road_id, vehicle_count, avg_speed_kmph, density, congestion_level, recorded_at
FROM traffic_readings
ORDER BY road_id, recorded_at DESC;

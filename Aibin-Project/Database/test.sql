-- =========================================
-- TRAFFIC CONGESTION DATABASE TESTS
-- EXISTING M1 DATABASE VERIFICATION
-- =========================================


-- =========================================
-- 1. VERIFY STAGING DATA
-- =========================================

SELECT COUNT(*) AS total_rows
FROM traffic_staging;

SELECT *
FROM traffic_staging
LIMIT 10;


-- =========================================
-- 2. INSERT / VERIFY ROADS
-- =========================================

INSERT INTO roads
    (road_code, road_name, road_description)
SELECT DISTINCT
    road_code,
    road_name,
    road_description
FROM traffic_staging
WHERE road_code IS NOT NULL
ON CONFLICT (road_code) DO NOTHING;

SELECT *
FROM roads
ORDER BY road_id;


-- =========================================
-- 3. INSERT / VERIFY SENSORS
-- =========================================

INSERT INTO sensors
(
    road_id,
    sensor_code,
    sensor_name,
    sensor_type,
    location,
    status
)
SELECT DISTINCT
    r.road_id,
    ts.sensor_code,
    ts.sensor_name,
    ts.sensor_type,
    ts.location,
    ts.status
FROM traffic_staging ts
JOIN roads r
    ON r.road_code = ts.road_code
WHERE ts.sensor_code IS NOT NULL
ON CONFLICT (sensor_code) DO NOTHING;

SELECT COUNT(*) AS total_sensors
FROM sensors;


-- =========================================
-- 4. VERIFY TRAFFIC READINGS
-- =========================================

SELECT *
FROM traffic_readings
ORDER BY timestamp DESC
LIMIT 10;

SELECT COUNT(*) AS total_readings
FROM traffic_readings;

SELECT
    s.road_id,
    COUNT(*) AS readings
FROM traffic_readings tr
JOIN sensors s
    ON tr.sensor_id = s.sensor_id
GROUP BY s.road_id
ORDER BY s.road_id;


-- =========================================
-- 5. FIX DUPLICATE ACTIVE CAPACITIES
-- =========================================

DELETE FROM road_capacity a
USING road_capacity b
WHERE a.road_id = b.road_id
  AND a.effective_to IS NULL
  AND b.effective_to IS NULL
  AND a.capacity_id < b.capacity_id;


-- =========================================
-- 6. PREVENT FUTURE DUPLICATE ACTIVE CAPACITIES
-- =========================================

CREATE UNIQUE INDEX IF NOT EXISTS uq_road_capacity_active
ON road_capacity(road_id)
WHERE effective_to IS NULL;


-- =========================================
-- 7. VERIFY ROAD CAPACITY
-- =========================================

SELECT *
FROM road_capacity
ORDER BY road_id, capacity_id;

SELECT
    road_id,
    COUNT(*) AS active_capacity_records
FROM road_capacity
WHERE effective_to IS NULL
GROUP BY road_id
ORDER BY road_id;


-- =========================================
-- 8. ROAD UTILIZATION TEST
-- =========================================

SELECT
    s.road_id,
    ROUND(AVG(tr.vehicle_count), 2) AS avg_vehicle_count,
    rc.vehicle_capacity,
    ROUND(
        (AVG(tr.vehicle_count) / rc.vehicle_capacity) * 100,
        2
    ) AS utilization_percent
FROM traffic_readings tr
JOIN sensors s
    ON tr.sensor_id = s.sensor_id
JOIN road_capacity rc
    ON s.road_id = rc.road_id
   AND rc.effective_to IS NULL
GROUP BY
    s.road_id,
    rc.vehicle_capacity
ORDER BY utilization_percent DESC;


-- =========================================
-- 9. QUERY PERFORMANCE INDEXES
-- =========================================

CREATE INDEX IF NOT EXISTS idx_traffic_readings_timestamp
ON traffic_readings(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_traffic_readings_sensor
ON traffic_readings(sensor_id);

CREATE INDEX IF NOT EXISTS idx_congestion_history_road_recorded
ON congestion_history(road_id, recorded_at DESC);


-- =========================================
-- 10. QUERY PERFORMANCE TESTS
-- =========================================

EXPLAIN ANALYZE
SELECT *
FROM traffic_readings
ORDER BY timestamp DESC
LIMIT 10;

EXPLAIN ANALYZE
SELECT
    s.road_id,
    COUNT(*) AS readings
FROM traffic_readings tr
JOIN sensors s
    ON tr.sensor_id = s.sensor_id
GROUP BY s.road_id
ORDER BY s.road_id;

EXPLAIN ANALYZE
SELECT *
FROM congestion_history
WHERE road_id = 1
ORDER BY recorded_at DESC
LIMIT 10;


-- =========================================
-- 11. VERIFY ALL TABLES
-- =========================================

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


-- =========================================
-- 12. FINAL DATABASE CHECK
-- =========================================

SELECT version();

SELECT current_database();


-- =========================================
-- MILESTONE 2 - DAY 2
-- HISTORICAL DATA VERIFICATION
-- =========================================


-- Total historical records

SELECT COUNT(*) AS total_historical_records
FROM traffic_readings;


-- Historical date range

SELECT
    MIN(timestamp) AS earliest_timestamp,
    MAX(timestamp) AS latest_timestamp
FROM traffic_readings;


-- Records available for each sensor

SELECT
    sensor_id,
    COUNT(*) AS record_count,
    MIN(timestamp) AS earliest_timestamp,
    MAX(timestamp) AS latest_timestamp
FROM traffic_readings
GROUP BY sensor_id
ORDER BY sensor_id;


-- Sample historical records

SELECT
    reading_id,
    sensor_id,
    source_record_id,
    timestamp,
    vehicle_count,
    density,
    congestion_level
FROM traffic_readings
ORDER BY timestamp
LIMIT 20;


-- Check duplicate source records

SELECT
    source_record_id,
    COUNT(*) AS duplicate_count
FROM traffic_readings
GROUP BY source_record_id
HAVING COUNT(*) > 1;


-- Check invalid vehicle counts

SELECT COUNT(*) AS invalid_vehicle_counts
FROM traffic_readings
WHERE vehicle_count < 0;


-- Check invalid density values

SELECT COUNT(*) AS invalid_density
FROM traffic_readings
WHERE density < 0
   OR density > 1;


-- Congestion-level distribution

SELECT
    congestion_level,
    COUNT(*) AS record_count
FROM traffic_readings
GROUP BY congestion_level
ORDER BY congestion_level;


-- Daily historical records

SELECT
    DATE(timestamp) AS traffic_date,
    COUNT(*) AS readings
FROM traffic_readings
GROUP BY DATE(timestamp)
ORDER BY traffic_date;


-- Hourly historical records

SELECT
    DATE_TRUNC('hour', timestamp) AS traffic_hour,
    COUNT(*) AS readings
FROM traffic_readings
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY traffic_hour
LIMIT 50;


-- =========================================
-- MILESTONE 2 - DAY 3
-- DATA QUALITY CHECK
-- =========================================


-- Check missing timestamps

SELECT COUNT(*) AS missing_timestamps
FROM traffic_readings
WHERE timestamp IS NULL;


-- Check duplicate source records

SELECT
    source_record_id,
    COUNT(*) AS duplicate_count
FROM traffic_readings
GROUP BY source_record_id
HAVING COUNT(*) > 1;


-- Check invalid vehicle counts

SELECT COUNT(*) AS invalid_vehicle_counts
FROM traffic_readings
WHERE vehicle_count < 0;


-- Check invalid density

SELECT COUNT(*) AS invalid_density
FROM traffic_readings
WHERE density < 0
   OR density > 1;


-- Check invalid congestion levels

SELECT COUNT(*) AS invalid_congestion_levels
FROM traffic_readings
WHERE congestion_level IS NOT NULL
  AND congestion_level NOT IN
      ('LOW', 'MEDIUM', 'HIGH', 'SEVERE');


-- =========================================
-- MILESTONE 2 - DAY 4
-- ROAD CONDITIONS VERIFICATION
-- =========================================


-- Verify road-condition data

SELECT *
FROM road_conditions;


-- Verify road-condition records in order

SELECT
    condition_id,
    road_id,
    condition_status,
    description,
    start_time,
    end_time,
    created_at
FROM road_conditions
ORDER BY condition_id;


-- Verify road conditions by road

SELECT
    road_id,
    condition_status,
    description,
    start_time,
    end_time
FROM road_conditions
ORDER BY road_id, start_time;
-- TrafficVision AI
-- M4: Database Validation Tests
-- Run against the trafficvision database.

-- 1. Validate road IDs
SELECT
    COUNT(*) AS total_roads,
    COUNT(*) FILTER (WHERE road_id IS NULL) AS missing_road_ids,
    COUNT(DISTINCT road_id) AS unique_road_ids
FROM roads;

-- 2. Validate sensor IDs
SELECT
    COUNT(*) AS total_sensors,
    COUNT(*) FILTER (WHERE sensor_id IS NULL) AS missing_sensor_ids,
    COUNT(DISTINCT sensor_id) AS unique_sensor_ids
FROM sensors;

-- 3. Validate traffic reading data quality
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE sensor_id IS NULL) AS missing_sensor_ids,
    COUNT(*) FILTER (WHERE "timestamp" IS NULL) AS missing_timestamps,
    COUNT(*) FILTER (WHERE reading_id IS NULL) AS missing_reading_ids
FROM traffic_readings;

-- 4. Validate congestion history data quality
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE road_id IS NULL) AS missing_road_ids,
    COUNT(*) FILTER (WHERE recorded_at IS NULL) AS missing_recorded_at,
    COUNT(*) FILTER (WHERE congestion_level IS NULL) AS missing_levels,
    COUNT(*) FILTER (WHERE density IS NULL) AS missing_density,
    COUNT(*) FILTER (
        WHERE density < 0 OR density > 1
    ) AS invalid_density
FROM congestion_history;

-- 5. Check congestion history references
SELECT COUNT(*) AS history_without_road
FROM congestion_history ch
LEFT JOIN roads r ON ch.road_id = r.road_id
WHERE r.road_id IS NULL;

-- 6. Check traffic readings references
SELECT COUNT(*) AS readings_without_sensor
FROM traffic_readings tr
LEFT JOIN sensors s ON tr.sensor_id = s.sensor_id
WHERE s.sensor_id IS NULL;
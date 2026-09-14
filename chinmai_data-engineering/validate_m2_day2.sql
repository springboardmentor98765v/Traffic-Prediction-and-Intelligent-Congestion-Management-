-- M2 Day 2 validation queries

SELECT COUNT(*) AS total_historical_records FROM traffic_history;

SELECT MIN(reading_timestamp) AS earliest_record,
       MAX(reading_timestamp) AS latest_record
FROM traffic_history;

SELECT COUNT(DISTINCT road_id) AS roads,
       COUNT(DISTINCT sensor_id) AS sensors
FROM traffic_history;

SELECT road_id, COUNT(*) AS record_count
FROM traffic_history
GROUP BY road_id
ORDER BY road_id;

SELECT congestion_level, COUNT(*) AS record_count
FROM traffic_history
GROUP BY congestion_level
ORDER BY congestion_level;

SELECT COUNT(*) AS invalid_records
FROM traffic_history
WHERE vehicle_count < 0
   OR avg_speed_kmph < 0
   OR road_capacity <= 0
   OR traffic_density_vehicles_per_km < 0;

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'traffic_history'
  AND column_name IN ('reading_timestamp', 'created_at')
ORDER BY column_name;

SELECT indexname
FROM pg_indexes
WHERE tablename = 'traffic_history'
ORDER BY indexname;

SELECT road_id, reading_timestamp, vehicle_count,
       avg_speed_kmph, traffic_density_vehicles_per_km, congestion_level
FROM traffic_history
ORDER BY reading_timestamp DESC
LIMIT 10;

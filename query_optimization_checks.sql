-- =====================================================
-- TrafficVision AI — Day 6 Query Optimization Checks
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- =====================================================

-- ---------------------------------------------------------
-- CHECK 1: Is the "latest reading per road" query using the index?
-- (This is the query behind /api/v1/traffic/live)
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT DISTINCT ON (road_id)
    road_id, vehicle_count, density, congestion_level, recorded_at
FROM traffic_readings
ORDER BY road_id, recorded_at DESC;

-- WHAT TO LOOK FOR in the output:
--   "Index Scan using idx_traffic_road_time" -> GOOD, the Day 1 index is being used
--   "Seq Scan on traffic_readings"           -> BAD, it's scanning the whole table
--
-- If you see Seq Scan instead of Index Scan, the table may still be too
-- small for PostgreSQL to bother using the index (it sometimes decides
-- a full scan is faster on small tables) — this is normal at this data
-- volume and will resolve itself as more rows accumulate.


-- ---------------------------------------------------------
-- CHECK 2: Road detail + history query (behind /traffic/road/{id})
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT vehicle_count, density, congestion_level, recorded_at
FROM traffic_readings
WHERE road_id = 1
ORDER BY recorded_at DESC
LIMIT 20;

-- Same idea: idx_traffic_road_time should be used here, since the
-- WHERE clause filters on road_id and ORDER BY uses recorded_at —
-- exactly the two columns the index was built on.


-- ---------------------------------------------------------
-- CHECK 3: Density summary aggregate query (behind /traffic/density)
-- ---------------------------------------------------------
EXPLAIN ANALYZE
WITH latest AS (
    SELECT DISTINCT ON (road_id) road_id, density, congestion_level
    FROM traffic_readings
    ORDER BY road_id, recorded_at DESC
)
SELECT
    ROUND(AVG(density), 2) AS avg_density,
    COUNT(*) AS total_roads_monitored,
    COUNT(*) FILTER (WHERE congestion_level = 'LOW') AS low_count,
    COUNT(*) FILTER (WHERE congestion_level = 'MODERATE') AS moderate_count,
    COUNT(*) FILTER (WHERE congestion_level = 'HIGH') AS high_count,
    COUNT(*) FILTER (WHERE congestion_level = 'SEVERE') AS severe_count
FROM latest;

-- This query reuses the same DISTINCT ON pattern inside a CTE (WITH ...),
-- so it benefits from the same index as Check 1.


-- ---------------------------------------------------------
-- OPTIMIZATION APPLIED: Additional index for growing data volume
-- ---------------------------------------------------------
-- As traffic_readings grows into millions of rows (real production
-- scale), a covering index that includes congestion_level speeds up
-- the density-summary aggregate query, since it can read the level
-- straight from the index without touching the full table row.

CREATE INDEX IF NOT EXISTS idx_traffic_road_time_level
ON traffic_readings (road_id, recorded_at DESC, congestion_level);

-- Re-run Check 3's EXPLAIN ANALYZE after adding this index and compare
-- the "Execution Time" line before vs after.

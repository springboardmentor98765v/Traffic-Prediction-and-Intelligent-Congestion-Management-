-- =====================================================
-- TrafficVision AI — Milestone 2, Day 6
-- Query Optimization Checks
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- =====================================================

-- ---------------------------------------------------------
-- CHECK 1: Duplicate-detection query (from clean_historical_data.py)
-- At ~40,000 rows, is this still fast, and does it use an index?
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT road_id, recorded_at, COUNT(*) AS duplicate_count
FROM traffic_readings
GROUP BY road_id, recorded_at
HAVING COUNT(*) > 1;

-- WHAT TO LOOK FOR: this GROUP BY benefits from the same
-- idx_traffic_road_time index built in Milestone 1 Day 1, since it's
-- grouping on (road_id, recorded_at) — exactly the index's columns.


-- ---------------------------------------------------------
-- CHECK 2: Gap-detection query (uses LAG window function)
-- Window functions can be expensive — verify it's still reasonable.
-- ---------------------------------------------------------
EXPLAIN ANALYZE
WITH ordered AS (
    SELECT
        road_id,
        recorded_at,
        LAG(recorded_at) OVER (PARTITION BY road_id ORDER BY recorded_at) AS prev_recorded_at
    FROM traffic_readings
)
SELECT road_id, prev_recorded_at, recorded_at,
       EXTRACT(EPOCH FROM (recorded_at - prev_recorded_at)) / 60 AS gap_minutes
FROM ordered
WHERE prev_recorded_at IS NOT NULL
  AND EXTRACT(EPOCH FROM (recorded_at - prev_recorded_at)) / 60 > 15
ORDER BY gap_minutes DESC
LIMIT 20;


-- ---------------------------------------------------------
-- CHECK 3: The new /traffic/features query (Day 5) — hour + weekday grouping
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT EXTRACT(HOUR FROM recorded_at)::int AS hour,
       ROUND(AVG(density), 2) AS avg_density
FROM traffic_readings
WHERE road_id = 1
GROUP BY hour
ORDER BY hour;

-- These queries filter by road_id first (using the index), then group
-- by an EXTRACTed value — the initial filter is what benefits most
-- from indexing; the grouping itself operates on the already-reduced
-- row set for that one road, which is small and fast regardless.

-- =====================================================
-- TrafficVision AI — Milestone 2, Day 5
-- Query Performance Checks + Materialized View
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- =====================================================

-- ---------------------------------------------------------
-- CHECK 1: How fast is /traffic/aggregate at current data volume?
-- (Run this BEFORE creating the materialized view below, to have a
--  baseline to compare against)
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT
    date_trunc('day', recorded_at) AS bucket,
    ROUND(AVG(density), 2) AS avg_density,
    ROUND(AVG(vehicle_count), 0) AS avg_vehicle_count,
    COUNT(*) AS reading_count
FROM traffic_readings
WHERE road_id = 1
GROUP BY bucket
ORDER BY bucket ASC;

-- WHAT TO LOOK FOR: at ~40,000 rows, this should still be fast
-- (single-digit milliseconds), but this query recomputes the
-- aggregation from scratch every single time it's called. As data
-- grows into millions of rows, that becomes wasteful — most of that
-- historical data never changes, so recalculating it repeatedly is
-- pure overhead.


-- ---------------------------------------------------------
-- OPTIMIZATION: Materialized view for feature-engineering queries
-- A materialized view pre-computes and STORES the aggregation result,
-- instead of recalculating it from raw rows on every request. This
-- trades a small amount of staleness (only as fresh as the last
-- refresh) for a big speed improvement on repeated reads — exactly
-- the trade-off Intern 3's feature engineering can afford, since
-- training doesn't need up-to-the-second freshness.
-- ---------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS traffic_daily_summary AS
SELECT
    road_id,
    date_trunc('day', recorded_at) AS day,
    EXTRACT(DOW FROM recorded_at) AS day_of_week,
    ROUND(AVG(density), 2) AS avg_density,
    ROUND(AVG(vehicle_count), 0) AS avg_vehicle_count,
    ROUND(MAX(density), 2) AS max_density,
    COUNT(*) AS reading_count
FROM traffic_readings
GROUP BY road_id, day, day_of_week;

-- Index the materialized view so lookups by road_id are fast too
CREATE INDEX IF NOT EXISTS idx_traffic_daily_summary_road
ON traffic_daily_summary (road_id, day);


-- ---------------------------------------------------------
-- CHECK 2: Compare speed — querying the materialized view instead
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT * FROM traffic_daily_summary WHERE road_id = 1 ORDER BY day ASC;

-- Compare this "Execution Time" to Check 1's — the materialized view
-- should be noticeably faster since it's reading pre-computed rows
-- instead of scanning and aggregating raw data every time.


-- ---------------------------------------------------------
-- MAINTENANCE NOTE: materialized views don't auto-update
-- Since historical data doesn't change often (it's backfilled once),
-- a manual refresh whenever new historical data is generated is fine
-- for this milestone's scope:
-- ---------------------------------------------------------
-- REFRESH MATERIALIZED VIEW traffic_daily_summary;

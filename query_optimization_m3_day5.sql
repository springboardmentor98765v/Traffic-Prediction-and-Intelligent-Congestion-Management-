-- =====================================================
-- TrafficVision AI — Milestone 3, Day 5
-- Analytics Query Performance Checks
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- =====================================================

-- ---------------------------------------------------------
-- CHECK 1: Heatmap's grouped query (road_id + hour, across ALL roads)
-- This is the most expensive Analytics query — grouping the entire
-- table by two dimensions simultaneously.
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT road_id, EXTRACT(HOUR FROM recorded_at)::int AS bucket,
       ROUND(AVG(density), 2) AS avg_density
FROM traffic_readings
GROUP BY road_id, bucket
ORDER BY road_id, bucket;

-- WHAT TO LOOK FOR: this scans the FULL table (no WHERE clause, since
-- the heatmap covers all-time data by design) — unlike per-road
-- queries, road_id isn't filtered here, only grouped. This is exactly
-- why Day 5 added Redis caching to this endpoint (60s TTL) — the query
-- itself can't be made much faster with indexing alone, since it
-- inherently needs to touch every row once.


-- ---------------------------------------------------------
-- CHECK 2: Reports query (date-range filter across all roads)
-- ---------------------------------------------------------
EXPLAIN ANALYZE
SELECT r.road_name, tr.road_id, tr.vehicle_count, tr.density,
       tr.congestion_level, tr.recorded_at
FROM traffic_readings tr
JOIN roads r ON r.road_id = tr.road_id
WHERE tr.recorded_at >= NOW() - INTERVAL '7 days'
ORDER BY tr.road_id, tr.recorded_at ASC;

-- This DOES benefit from filtering, but still returns a large row
-- count across all roads combined (unlike /traffic/history's Day 7
-- cap, which applies per single road). Worth monitoring row count
-- growth here as more historical data accumulates.


-- ---------------------------------------------------------
-- OPTIMIZATION CONSIDERATION: should /analytics/reports also cap rows?
-- Per the lesson learned in Milestone 2, Day 7 (the /traffic/history
-- unbounded-response defect), this is worth flagging: /analytics/reports
-- currently has NO row limit either. For a "week" range across 5 roads
-- at 5-minute intervals, that's roughly 5 * 7 * 24 * 12 = ~10,080 rows —
-- currently fine, but if roads or data frequency grow substantially,
-- the same unbounded-response risk applies here too. Flagged as a
-- known consideration for Day 6/7 review, not yet fixed, since current
-- volume doesn't yet demonstrate an actual problem.
-- ---------------------------------------------------------

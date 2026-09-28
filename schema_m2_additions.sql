-- =====================================================
-- TrafficVision AI — Milestone 2 Schema Additions
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- Run this AFTER Milestone 1's schema.sql is already loaded.
-- =====================================================

-- ---------------------------------------------------------
-- NEW TABLE: road_conditions
-- Tracks closures, construction, hazards — new for Milestone 2.
-- Consumed by: Intern 1's /route/conditions endpoint
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS road_conditions (
    condition_id    SERIAL PRIMARY KEY,
    road_id         INT NOT NULL REFERENCES roads(road_id) ON DELETE CASCADE,
    status          VARCHAR(30) NOT NULL DEFAULT 'CLEAR',  -- CLEAR / CLOSED / CONSTRUCTION / HAZARD
    notes           TEXT,
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- One index for "get the current condition of a specific road" — the
-- exact query pattern /traffic/road-condition/{road_id} will use.
CREATE INDEX IF NOT EXISTS idx_road_conditions_road
ON road_conditions (road_id, updated_at DESC);


-- ---------------------------------------------------------
-- VERIFY: traffic_readings is ready for time-range queries
-- (No schema change needed — Milestone 1's idx_traffic_road_time
--  already covers (road_id, recorded_at DESC), which range queries
--  also benefit from. We verify with EXPLAIN ANALYZE on Day 3 once
--  the /traffic/history endpoint exists.)
-- ---------------------------------------------------------
-- Sanity check: confirm the Milestone 1 index still exists
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'traffic_readings';


-- ---------------------------------------------------------
-- Seed a starting condition row for every existing road
-- (defaults everything to CLEAR so the API has data to return
--  from Day 1, before Day 4's real ingestion logic is built)
-- ---------------------------------------------------------
INSERT INTO road_conditions (road_id, status, notes)
SELECT road_id, 'CLEAR', 'No known issues'
FROM roads
WHERE road_id NOT IN (SELECT road_id FROM road_conditions);

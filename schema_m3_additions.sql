-- =====================================================
-- TrafficVision AI — Milestone 3 Schema Additions
-- Owner: Intern 2 (Data Engineering & Traffic Monitoring)
-- Run this AFTER Milestone 1 + Milestone 2 schemas are loaded.
-- =====================================================

-- ---------------------------------------------------------
-- NEW TABLE: alert_thresholds
-- Defines the density level above which a road should trigger a
-- congestion alert. One row per road; a NULL road_id row acts as
-- the global default fallback for any road without its own entry.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS alert_thresholds (
    threshold_id    SERIAL PRIMARY KEY,
    road_id         INT REFERENCES roads(road_id) ON DELETE CASCADE,  -- NULL = global default
    density_threshold  NUMERIC(5,2) NOT NULL DEFAULT 85.0,  -- matches SEVERE level by default
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Only one active threshold per road (or one global default)
CREATE UNIQUE INDEX IF NOT EXISTS idx_alert_thresholds_road
ON alert_thresholds (COALESCE(road_id, -1));

-- ---------------------------------------------------------
-- Seed a sensible global default (SEVERE-level density = 85)
-- ---------------------------------------------------------
INSERT INTO alert_thresholds (road_id, density_threshold, is_active)
SELECT NULL, 85.0, TRUE
WHERE NOT EXISTS (SELECT 1 FROM alert_thresholds WHERE road_id IS NULL);

-- ---------------------------------------------------------
-- Seed per-road thresholds — highways tolerate higher density
-- before it's genuinely alarming; local roads trigger earlier
-- ---------------------------------------------------------
INSERT INTO alert_thresholds (road_id, density_threshold, is_active)
SELECT road_id,
       CASE road_type
           WHEN 'highway' THEN 90.0
           WHEN 'arterial' THEN 85.0
           WHEN 'local' THEN 75.0
           ELSE 85.0
       END,
       TRUE
FROM roads
WHERE road_id NOT IN (SELECT road_id FROM alert_thresholds WHERE road_id IS NOT NULL);

-- Verify
SELECT at.road_id, r.road_name, r.road_type, at.density_threshold
FROM alert_thresholds at
LEFT JOIN roads r ON r.road_id = at.road_id
ORDER BY at.road_id NULLS FIRST;

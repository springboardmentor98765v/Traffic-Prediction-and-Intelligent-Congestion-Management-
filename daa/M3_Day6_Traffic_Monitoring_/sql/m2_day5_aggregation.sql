-- ============================================================
-- M2 DAY 5 - TRAFFIC AGGREGATION
-- ============================================================
-- Existing tables from milestone_2_schema.sql:
--   hourly_traffic_metrics
--   daily_traffic_metrics
--
-- This file adds/ensures the indexes needed for fast
-- road/time aggregation lookups.
-- ============================================================


-- ------------------------------------------------------------
-- 1. HOURLY METRICS INDEX
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_hourly_metrics_road_time
    ON hourly_traffic_metrics
    (road_id, metric_timestamp DESC);


-- ------------------------------------------------------------
-- 2. DAILY METRICS INDEX
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_daily_metrics_road_date
    ON daily_traffic_metrics
    (road_id, metric_date DESC);


-- ------------------------------------------------------------
-- 3. HISTORICAL DATA INDEX
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_traffic_history_road_time
    ON traffic_history
    (road_id, reading_timestamp DESC);


-- ------------------------------------------------------------
-- 4. HISTORICAL TIME INDEX
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_traffic_history_timestamp
    ON traffic_history
    (reading_timestamp DESC);


-- ============================================================
-- END M2 DAY 5 INDEX SETUP
-- ============================================================
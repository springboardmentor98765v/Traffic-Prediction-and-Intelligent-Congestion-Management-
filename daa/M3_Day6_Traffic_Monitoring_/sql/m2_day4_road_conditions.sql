-- ============================================================
-- M2 DAY 4 - ROAD CONDITIONS
-- Uses the existing M2 road_conditions schema extension.
-- ============================================================

CREATE TABLE IF NOT EXISTS road_conditions (
    condition_id BIGSERIAL PRIMARY KEY,
    road_id VARCHAR(20) NOT NULL,
    condition_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    road_condition VARCHAR(50) NOT NULL,
    road_status VARCHAR(30) NOT NULL,
    incident_type VARCHAR(50),
    description TEXT,
    source VARCHAR(100) NOT NULL DEFAULT 'manual_or_external',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_road_conditions_road
        FOREIGN KEY (road_id) REFERENCES roads(road_id)
);

CREATE INDEX IF NOT EXISTS idx_road_conditions_road_time
    ON road_conditions (road_id, condition_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_road_conditions_active
    ON road_conditions (road_id, road_status, condition_timestamp DESC);

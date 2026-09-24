-- TrafficVision AI - Migration 003: Create Alerts and Alert Reads Tables (Milestone 3)

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(36) PRIMARY KEY,
    type VARCHAR(30) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    road_id VARCHAR(50) NOT NULL,
    message VARCHAR(500) NOT NULL,
    target_role VARCHAR(20) NOT NULL DEFAULT 'public',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Alert Reads table (Per-user read tracking)
CREATE TABLE IF NOT EXISTS alert_reads (
    id VARCHAR(36) PRIMARY KEY,
    alert_id VARCHAR(36) NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for high-performance querying and polling
CREATE INDEX IF NOT EXISTS idx_alerts_road_id ON alerts(road_id);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type);
CREATE INDEX IF NOT EXISTS idx_alerts_target_role ON alerts(target_role);
CREATE INDEX IF NOT EXISTS idx_alerts_is_active ON alerts(is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alert_reads_alert_user ON alert_reads(alert_id, user_id);

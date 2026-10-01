import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATE_DB_PATH = Path(os.getenv(
    "TRAFFICVISION_STATE_DB",
    str(PROJECT_ROOT / ".trafficvision" / "state.sqlite3"),
))

SCHEMA = """
CREATE TABLE IF NOT EXISTS auth_sessions (
    refresh_jti TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    revoked_at INTEGER
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_email ON auth_sessions(email);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    source_key TEXT UNIQUE,
    road_id TEXT NOT NULL,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    vehicle_count INTEGER,
    density REAL,
    avg_speed_kmph REAL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    is_read INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_alerts_road_time ON alerts(road_id, created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status, is_read);

CREATE TABLE IF NOT EXISTS alert_reads (
    alert_id TEXT PRIMARY KEY,
    read_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS road_conditions (
    road_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    notes TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS route_cache (
    route_id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


@contextmanager
def open_state():
    path = Path(STATE_DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.executescript(SCHEMA)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
"""
TrafficVision AI — Congestion-Threshold Breach Feed (Milestone 3, Day 2)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Watches the LATEST live reading for every road, compares it against
    that road's configured threshold (alert_thresholds table, Day 1),
    and — when a breach is detected — calls Intern 1's alert-creation
    endpoint (POST /api/v1/alerts) to raise a congestion alert.

    This is a continuous feed (like ingest_live_data.py), checking
    every N seconds, since live density changes constantly.

Cooldown logic:
    Without a cooldown, a road sitting just above its threshold would
    generate a NEW alert every single check cycle — alert spam, which
    the SRS's own Risks section (15) explicitly warns about ("Alert
    'noise' overwhelms users"). A simple in-memory cooldown means each
    road can only trigger one alert every COOLDOWN_SECONDS, even if it
    stays breached the whole time.

Requirements:
    pip install psycopg2-binary requests

Run (with ingest_live_data.py and alert_service_stub.py already running):
    python threshold_monitor.py
"""

import time
from datetime import datetime, timedelta

import psycopg2
import psycopg2.extras
import requests

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "trafficvision",
    "user": "postgres",
    "password": "kitty@2211",  # <-- put your actual postgres password
}

ALERT_SERVICE_URL = "http://127.0.0.1:8100/api/v1/alerts"  # Intern 1's real service in production
CHECK_INTERVAL_SECONDS = 10
COOLDOWN_SECONDS = 60  # don't re-alert the same road more than once per minute

# Tracks the last time each road triggered an alert, to enforce cooldown
_last_alert_time = {}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def fetch_latest_readings_with_thresholds(conn):
    """
    For every road, get its MOST RECENT density reading and its
    configured threshold (falling back to the global default if the
    road has no specific threshold of its own).
    """
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            WITH latest AS (
                SELECT DISTINCT ON (road_id) road_id, density, recorded_at
                FROM traffic_readings
                ORDER BY road_id, recorded_at DESC
            ),
            thresholds AS (
                SELECT road_id, density_threshold
                FROM alert_thresholds
                WHERE road_id IS NOT NULL AND is_active = TRUE
            ),
            default_threshold AS (
                SELECT density_threshold FROM alert_thresholds
                WHERE road_id IS NULL AND is_active = TRUE
                LIMIT 1
            )
            SELECT
                l.road_id,
                r.road_name,
                l.density,
                l.recorded_at,
                COALESCE(t.density_threshold, (SELECT density_threshold FROM default_threshold)) AS threshold
            FROM latest l
            JOIN roads r ON r.road_id = l.road_id
            LEFT JOIN thresholds t ON t.road_id = l.road_id;
            """
        )
        return cur.fetchall()


def is_in_cooldown(road_id):
    last_time = _last_alert_time.get(road_id)
    if last_time is None:
        return False
    return (datetime.now() - last_time) < timedelta(seconds=COOLDOWN_SECONDS)


def raise_alert(road_id, road_name, density, threshold):
    """Calls the Alert Service's documented contract shape (SRS 7.1)."""
    payload = {
        "type": "congestion",
        "severity": "HIGH" if density < 95 else "SEVERE",
        "road_id": road_id,
        "message": f"{road_name} density at {density}% (threshold: {threshold}%)",
    }
    try:
        response = requests.post(ALERT_SERVICE_URL, json=payload, timeout=5)
        if response.status_code == 201:
            print(f"  -> Alert raised for {road_name}: {payload['message']}")
            _last_alert_time[road_id] = datetime.now()
        else:
            print(f"  -> Alert Service returned {response.status_code} for {road_name}")
    except requests.exceptions.ConnectionError:
        print(f"  -> Could not reach Alert Service at {ALERT_SERVICE_URL}. "
              f"Is alert_service_stub.py running on port 8100?")


def check_thresholds(conn):
    rows = fetch_latest_readings_with_thresholds(conn)
    breaches_found = 0

    for row in rows:
        if row["density"] is None or row["threshold"] is None:
            continue

        if row["density"] >= row["threshold"]:
            if is_in_cooldown(row["road_id"]):
                continue  # already alerted recently, skip to avoid spam
            breaches_found += 1
            raise_alert(row["road_id"], row["road_name"], row["density"], row["threshold"])

    return breaches_found


def main():
    print("Congestion-threshold monitor starting...")
    print(f"Checking every {CHECK_INTERVAL_SECONDS}s, cooldown {COOLDOWN_SECONDS}s per road.")
    print("Press Ctrl+C to stop.\n")

    conn = get_connection()
    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            breaches = check_thresholds(conn)
            status = f"{breaches} breach(es) found" if breaches else "all roads within threshold"
            print(f"[{timestamp}] Checked all roads — {status}")
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

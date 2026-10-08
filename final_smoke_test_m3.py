"""
TrafficVision AI — Final Smoke Test, Milestone 3 (Day 7)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Three things the SRS requires for Day 7:
      1. REGRESSION on Milestone 1 endpoints (live, road, tracking,
         density, by-name)
      2. REGRESSION on Milestone 2 endpoints (history, aggregate,
         features, road-condition)
      3. Validation of every NEW Milestone 3 endpoint (trends,
         heatmap, reports) plus the threshold-monitor/alert-stub
         integration from Day 2

    Extends the pattern from Milestone 2's final_smoke_test_m2.py.

Requirements:
    pip install requests

Run (with main.py, ingest_live_data.py, and optionally
     alert_service_stub.py + threshold_monitor.py already running):
    python final_smoke_test_m3.py
"""

import sys
import requests

BASE = "http://127.0.0.1:8000"
ALERT_STUB_BASE = "http://127.0.0.1:8100"
results = []


def check(description, condition):
    status = "PASS" if condition else "FAIL"
    results.append((status, description))
    print(f"[{status}] {description}")


def run_m1_regression():
    print("\n--- REGRESSION: Milestone 1 endpoints ---")
    r = requests.get(f"{BASE}/", timeout=5)
    check("Root endpoint responds 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/live", timeout=5)
    check("M1: /traffic/live returns 200", r.status_code == 200)
    check("M1: /traffic/live returns a non-empty list", len(r.json()) > 0 if r.status_code == 200 else False)

    r = requests.get(f"{BASE}/api/v1/traffic/road/1", timeout=5)
    check("M1: /traffic/road/1 returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/road/99999", timeout=5)
    check("M1: /traffic/road/99999 returns 404", r.status_code == 404)

    r = requests.get(f"{BASE}/api/v1/traffic/road/1/tracking", timeout=5)
    check("M1: /traffic/road/1/tracking returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/density", timeout=5)
    check("M1: /traffic/density returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/road/by-name/anna", timeout=5)
    check("M1: search-by-name returns 200", r.status_code == 200)


def run_m2_regression():
    print("\n--- REGRESSION: Milestone 2 endpoints ---")
    r = requests.get(
        f"{BASE}/api/v1/traffic/history",
        params={"road_id": 1, "start": "2026-08-01T00:00:00", "end": "2026-09-19T00:00:00"},
        timeout=15,
    )
    check("M2: /traffic/history returns 200", r.status_code == 200)
    if r.status_code == 200:
        check("M2: /traffic/history has readings + truncation metadata",
              "readings" in r.json() and "truncated" in r.json())

    r = requests.get(f"{BASE}/api/v1/traffic/aggregate", params={"road_id": 1, "granularity": "day"}, timeout=10)
    check("M2: /traffic/aggregate returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/features/1", timeout=10)
    check("M2: /traffic/features/1 returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/road-condition/1", timeout=5)
    check("M2: /traffic/road-condition/1 returns 200", r.status_code == 200)


def run_m3_checks():
    print("\n--- NEW: Milestone 3 endpoints ---")

    # /analytics/trends
    r = requests.get(f"{BASE}/api/v1/analytics/trends", params={"road_id": 1, "range": "day"}, timeout=10)
    check("M3: /analytics/trends (day) returns 200", r.status_code == 200)
    if r.status_code == 200:
        points = r.json().get("points", [])
        check("M3: /analytics/trends (day) has 24 points", len(points) == 24)

    r = requests.get(f"{BASE}/api/v1/analytics/trends", params={"road_id": 1, "range": "Week"}, timeout=10)
    check("M3: /analytics/trends accepts 'Week' (case-insensitive)", r.status_code == 200)
    if r.status_code == 200:
        points = r.json().get("points", [])
        check("M3: /analytics/trends (week) has 7 points", len(points) == 7)

    # /analytics/heatmap
    r = requests.get(f"{BASE}/api/v1/analytics/heatmap", params={"range": "day"}, timeout=15)
    check("M3: /analytics/heatmap (day) returns 200", r.status_code == 200)
    if r.status_code == 200:
        data = r.json()
        check("M3: heatmap grid is a proper rectangle",
              all(len(row) == len(data["time_buckets"]) for row in data["values"]))
        check("M3: heatmap row count matches road count", len(data["values"]) == len(data["roads"]))

    r = requests.get(f"{BASE}/api/v1/analytics/heatmap", params={"range": "bogus"}, timeout=5)
    check("M3: /analytics/heatmap rejects invalid range with 400", r.status_code == 400)

    # /analytics/reports
    r = requests.get(f"{BASE}/api/v1/analytics/reports", params={"range": "week", "format": "csv"}, timeout=20)
    check("M3: /analytics/reports returns 200", r.status_code == 200)
    if r.status_code == 200:
        check("M3: reports response has X-Total-Rows header", "X-Total-Rows" in r.headers)
        check("M3: reports response has X-Truncated header", "X-Truncated" in r.headers)
        check("M3: reports content is actually CSV", r.text.startswith("road_name") or "," in r.text.split("\n")[0])

    r = requests.get(f"{BASE}/api/v1/analytics/reports", params={"range": "week", "format": "xlsx"}, timeout=5)
    check("M3: /analytics/reports rejects unsupported format with 400", r.status_code == 400)


def run_alert_integration_check():
    print("\n--- OPTIONAL: Alert Service stub integration (Day 2) ---")
    try:
        r = requests.get(f"{ALERT_STUB_BASE}/api/v1/alerts/active", timeout=3)
        check("Alert Service stub is reachable", r.status_code == 200)
    except requests.exceptions.ConnectionError:
        print("  (Alert Service stub not running — skipping this optional check)")


def print_summary():
    passed = sum(1 for s, _ in results if s == "PASS")
    failed = sum(1 for s, _ in results if s == "FAIL")
    print("\n" + "=" * 55)
    print(f"MILESTONE 3 FINAL SMOKE TEST: {passed} passed, {failed} failed")
    print("=" * 55)
    if failed:
        print("\nFailed checks:")
        for s, d in results:
            if s == "FAIL":
                print(f"  - {d}")
        sys.exit(1)
    print("\nAll checks passed. Milestone 3 data/analytics module ready for sign-off.")


if __name__ == "__main__":
    try:
        run_m1_regression()
        run_m2_regression()
        run_m3_checks()
        run_alert_integration_check()
    except requests.exceptions.ConnectionError:
        print("\nCould not connect. Is 'uvicorn main:app --reload' running on port 8000?")
        sys.exit(1)
    print_summary()

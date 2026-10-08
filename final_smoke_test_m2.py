"""
TrafficVision AI — Final Smoke Test, Milestone 2 (Day 7)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Two things the SRS requires for Day 7:
      1. REGRESSION check — confirm all Milestone 1 endpoints STILL
         work correctly, since Milestone 2 changes shouldn't have
         broken anything that already worked (SRS FR-10).
      2. Validate every NEW Milestone 2 endpoint end-to-end.

    This extends Milestone 1's final_smoke_test.py rather than
    replacing it — same pattern, more checks.

Requirements:
    pip install requests

Run (with main.py already running on port 8000):
    python final_smoke_test_m2.py
"""

import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(description, condition):
    status = "PASS" if condition else "FAIL"
    results.append((status, description))
    print(f"[{status}] {description}")


def run_regression_checks():
    """Milestone 1 endpoints — must still work after all M2 changes."""
    print("\n--- REGRESSION: Milestone 1 endpoints ---")

    r = requests.get(f"{BASE}/", timeout=5)
    check("Root endpoint responds 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/live", timeout=5)
    check("M1: /traffic/live still returns 200", r.status_code == 200)
    live_data = r.json() if r.status_code == 200 else []
    check("M1: /traffic/live still returns a non-empty list", len(live_data) > 0)

    r = requests.get(f"{BASE}/api/v1/traffic/road/1", timeout=5)
    check("M1: /traffic/road/1 still returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/road/99999", timeout=5)
    check("M1: /traffic/road/99999 still returns 404", r.status_code == 404)

    r = requests.get(f"{BASE}/api/v1/traffic/road/1/tracking", timeout=5)
    check("M1: /traffic/road/1/tracking still returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/density", timeout=5)
    check("M1: /traffic/density still returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/road/by-name/anna", timeout=5)
    check("M1: search-by-name still returns 200", r.status_code == 200)


def run_m2_checks():
    """New Milestone 2 endpoints — validate each one end-to-end."""
    print("\n--- NEW: Milestone 2 endpoints ---")

    r = requests.get(
        f"{BASE}/api/v1/traffic/history",
        params={"road_id": 1, "start": "2026-08-01T00:00:00", "end": "2026-09-19T00:00:00"},
        timeout=15,
    )
    check("M2: /traffic/history returns 200", r.status_code == 200)
    history_response = r.json() if r.status_code == 200 else {}
    history_data = history_response.get("readings", [])
    check("M2: /traffic/history returns readings", len(history_data) > 0)
    check("M2: /traffic/history response is capped by default limit",
          history_response.get("returned_count", 0) <= 5000)
    if history_data:
        required_fields = {"road_id", "timestamp", "vehicle_count", "density", "congestion_level"}
        check("M2: /traffic/history rows have contract fields",
              required_fields.issubset(set(history_data[0].keys())))

    r = requests.get(f"{BASE}/api/v1/traffic/history", params={"road_id": 1, "start": "2026-09-19T00:00:00", "end": "2026-08-01T00:00:00"}, timeout=5)
    check("M2: /traffic/history rejects start>end with 400", r.status_code == 400)

    r = requests.get(f"{BASE}/api/v1/traffic/aggregate", params={"road_id": 1, "granularity": "day"}, timeout=10)
    check("M2: /traffic/aggregate (day) returns 200", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/aggregate", params={"road_id": 1, "granularity": "Hour"}, timeout=10)
    check("M2: /traffic/aggregate accepts 'Hour' (Day 6 defect fix)", r.status_code == 200)

    r = requests.get(f"{BASE}/api/v1/traffic/aggregate", params={"road_id": 1, "granularity": "bogus"}, timeout=5)
    check("M2: /traffic/aggregate rejects invalid granularity with 400", r.status_code == 400)

    r = requests.get(f"{BASE}/api/v1/traffic/features/1", timeout=10)
    check("M2: /traffic/features/1 returns 200", r.status_code == 200)
    if r.status_code == 200:
        features = r.json()
        check("M2: /traffic/features has expected keys",
              {"avg_density_by_hour", "avg_density_by_weekday", "peak_hours"}.issubset(features.keys()))

    r = requests.get(f"{BASE}/api/v1/traffic/road-condition/1", timeout=5)
    check("M2: /traffic/road-condition/1 returns 200", r.status_code == 200)
    if r.status_code == 200:
        condition = r.json()
        check("M2: road-condition has expected shape",
              {"road_id", "status", "notes", "updated_at"}.issubset(condition.keys()))


def print_summary():
    passed = sum(1 for s, _ in results if s == "PASS")
    failed = sum(1 for s, _ in results if s == "FAIL")
    print("\n" + "=" * 55)
    print(f"MILESTONE 2 FINAL SMOKE TEST: {passed} passed, {failed} failed")
    print("=" * 55)
    if failed:
        print("\nFailed checks:")
        for s, d in results:
            if s == "FAIL":
                print(f"  - {d}")
        sys.exit(1)
    print("\nAll checks passed. Milestone 2 data module ready for sign-off.")


if __name__ == "__main__":
    try:
        run_regression_checks()
        run_m2_checks()
    except requests.exceptions.ConnectionError:
        print("\nCould not connect. Is 'uvicorn main:app --reload' running on port 8000?")
        sys.exit(1)
    print_summary()

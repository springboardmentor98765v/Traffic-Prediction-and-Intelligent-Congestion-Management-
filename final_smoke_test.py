"""
TrafficVision AI — Final Smoke Test (Day 7)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    A single script that hits EVERY endpoint of the Traffic Monitoring
    Service — both directly and through the Gateway — and confirms
    each one responds correctly. This is the "final validation" the
    SRS asks for on Day 7, run right before sign-off.

Requirements:
    pip install requests

Run (with ingest_live_data.py, main.py, and gateway.py all already running):
    python final_smoke_test.py
"""

import sys
import requests

DIRECT_BASE = "http://127.0.0.1:8000"
GATEWAY_BASE = "http://127.0.0.1:9000"

results = []


def check(description, condition):
    status = "PASS" if condition else "FAIL"
    results.append((status, description))
    print(f"[{status}] {description}")


def run_checks():
    # ---------------------------------------------------------
    # 1. Direct service health check
    # ---------------------------------------------------------
    try:
        r = requests.get(f"{DIRECT_BASE}/", timeout=5)
        check("Direct service root responds 200", r.status_code == 200)
    except requests.exceptions.ConnectionError:
        check("Direct service root responds 200", False)
        print("  -> Is 'uvicorn main:app --reload' running on port 8000?")
        return

    # ---------------------------------------------------------
    # 2. /traffic/live — direct
    # ---------------------------------------------------------
    r = requests.get(f"{DIRECT_BASE}/api/v1/traffic/live", timeout=5)
    check("GET /traffic/live returns 200 (direct)", r.status_code == 200)
    live_data = r.json()
    check("/traffic/live returns a non-empty list", isinstance(live_data, list) and len(live_data) > 0)

    if live_data:
        required_fields = {"road_id", "vehicle_count", "density", "congestion_level", "updated_at"}
        first_row_fields = set(live_data[0].keys())
        check("/traffic/live rows contain all contract fields", required_fields.issubset(first_row_fields))

    # ---------------------------------------------------------
    # 3. /traffic/road/{id} — direct, valid and invalid road
    # ---------------------------------------------------------
    r = requests.get(f"{DIRECT_BASE}/api/v1/traffic/road/1", timeout=5)
    check("GET /traffic/road/1 returns 200 for valid road", r.status_code == 200)

    r = requests.get(f"{DIRECT_BASE}/api/v1/traffic/road/99999", timeout=5)
    check("GET /traffic/road/99999 returns 404 for invalid road", r.status_code == 404)

    # ---------------------------------------------------------
    # 4. /traffic/road/{id}/tracking — direct
    # ---------------------------------------------------------
    r = requests.get(f"{DIRECT_BASE}/api/v1/traffic/road/1/tracking", timeout=5)
    check("GET /traffic/road/1/tracking returns 200", r.status_code == 200)
    if r.status_code == 200:
        tracking_data = r.json()
        check(
            "/tracking response contains utilization + state history",
            "current_utilization_percent" in tracking_data and "congestion_state_history" in tracking_data,
        )

    # ---------------------------------------------------------
    # 5. /traffic/density — direct
    # ---------------------------------------------------------
    r = requests.get(f"{DIRECT_BASE}/api/v1/traffic/density", timeout=5)
    check("GET /traffic/density returns 200", r.status_code == 200)

    # ---------------------------------------------------------
    # 6. Same endpoint via the GATEWAY, confirm matching structure
    # ---------------------------------------------------------
    try:
        r_gateway = requests.get(f"{GATEWAY_BASE}/api/v1/traffic/live", timeout=5)
        check("GET /traffic/live returns 200 (via Gateway)", r_gateway.status_code == 200)
        gateway_data = r_gateway.json()
        check(
            "Gateway response has the same number of roads as direct call",
            len(gateway_data) == len(live_data),
        )
    except requests.exceptions.ConnectionError:
        check("GET /traffic/live returns 200 (via Gateway)", False)
        print("  -> Is 'uvicorn gateway:app --reload --port 9000' running?")


def print_summary():
    passed = sum(1 for status, _ in results if status == "PASS")
    failed = sum(1 for status, _ in results if status == "FAIL")
    print("\n" + "=" * 50)
    print(f"SMOKE TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 50)
    if failed > 0:
        print("\nFailed checks:")
        for status, desc in results:
            if status == "FAIL":
                print(f"  - {desc}")
        sys.exit(1)
    else:
        print("\nAll checks passed. Module ready for sign-off.")


if __name__ == "__main__":
    run_checks()
    print_summary()

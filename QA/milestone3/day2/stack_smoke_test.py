"""Milestone 3 Day 2 — full local stack smoke test (M1 + M2 + M3).

Run after `docker compose -f docker-compose.dev.yml up -d`:

    python QA/milestone3/day2/stack_smoke_test.py [--base-url http://127.0.0.1:8000]

Stdlib only, so it runs on the host without installing anything. Exits
non-zero if any check fails.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qa_auth  # noqa: E402

ORIGIN = "11.9416,79.8083"
DESTINATION = "11.9350,79.8100"


def call(base, method, path, body=None, token=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    elapsed_ms = (time.perf_counter() - start) * 1000
    try:
        payload = json.loads(raw) if raw else None
    except ValueError:
        payload = raw.decode(errors="replace")
    return status, payload, elapsed_ms


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    base = parser.parse_args().base_url.rstrip("/")

    results = []

    def check(area, name, method, path, expect, body=None, token=None, headers=None):
        status, payload, ms = call(base, method, path, body, token, headers)
        ok = status == expect
        results.append((area, name, method, path, expect, status, ms, ok))
        return payload

    # --- System ---------------------------------------------------------
    check("System", "Health", "GET", "/health", 200)

    # --- M1: Auth + RBAC ------------------------------------------------
    # Registration is restricted to allow-listed domains (app/schemas/user.py).
    # `name` is stored as a unique username, so it must be unique per run too.
    run_id = uuid.uuid4().hex[:8]
    email = f"qa.m3d2.{run_id}@gmail.com"
    creds = {"email": email, "password": "QaPass#2026"}
    check(
        "M1 Auth",
        "Register",
        "POST",
        "/api/v1/auth/register",
        201,
        {"name": f"qa_m3d2_{run_id}", **creds},
    )
    login = check("M1 Auth", "Login", "POST", "/api/v1/auth/login", 200, creds) or {}
    access = login.get("access_token")
    refresh = login.get("refresh_token")
    check("M1 Auth", "Me (with token)", "GET", "/api/v1/auth/me", 200, token=access)
    check("M1 Auth", "Me (no token) rejected", "GET", "/api/v1/auth/me", 401)
    check("M1 Auth", "Refresh", "POST", "/api/v1/auth/refresh", 200, {"refresh_token": refresh})
    check(
        "M1 Auth",
        "Login wrong password rejected",
        "POST",
        "/api/v1/auth/login",
        401,
        {"email": email, "password": "wrong"},
    )

    # --- M1/M2: Traffic monitoring --------------------------------------
    check("M2 Traffic", "Live", "GET", "/api/v1/traffic/live", 200)
    check("M2 Traffic", "Road R001", "GET", "/api/v1/traffic/road/R001", 200)
    check("M2 Traffic", "Density", "GET", "/api/v1/traffic/density", 200)
    check("M2 Traffic", "History", "GET", "/api/v1/traffic/history?road_id=R001&limit=5", 200)
    check("M2 Traffic", "Aggregate", "GET", "/api/v1/traffic/aggregate?road_id=R001", 200)
    check("M2 Traffic", "Road condition", "GET", "/api/v1/traffic/road-condition/R001", 200)
    for period in ("hourly", "daily"):
        check(
            "M2 Traffic",
            f"{period.title()} metrics",
            "GET",
            f"/api/v1/traffic/metrics/{period}?road_id=R001&limit=5",
            200,
        )

    # --- M2: Prediction -------------------------------------------------
    check("M2 Predict", "Congestion (GET)", "GET", "/api/v1/predict/congestion?road_id=R001", 200)
    check(
        "M2 Predict",
        "Congestion (POST)",
        "POST",
        "/api/v1/predict/congestion",
        200,
        {
            "road_id": "R001",
            "vehicle_count": 80,
            "density": 16.0,
            "avg_speed_kmph": 22.0,
            "road_capacity": 100,
            "road_length_km": 5.0,
            "hour": 9,
            "day_of_week": 1,
            "is_weekend": 0,
        },
    )
    check("M2 Predict", "Peak hours", "GET", "/api/v1/predict/peak-hours?road_id=R001", 200)
    check("M2 Predict", "Delay", "GET", "/api/v1/predict/delay?road_id=R001", 200)

    # --- M2: Route analysis ---------------------------------------------
    q = f"origin={ORIGIN}&destination={DESTINATION}"
    for ep in ("optimize", "alternate", "travel-time", "conditions"):
        check("M2 Route", ep, "GET", f"/api/v1/route/{ep}?{q}", 200, token=access)
    check("M2 Route", "No token rejected", "GET", f"/api/v1/route/optimize?{q}", 401)
    check(
        "M2 Route",
        "Invalid coords rejected",
        "GET",
        "/api/v1/route/optimize?origin=abc&destination=xyz",
        400,
        token=access,
    )

    # --- M3: Alert Service ----------------------------------------------
    # Since the DEF-M3-005/012 fix: producers post with the internal service key, and
    # reads use the caller's JWT (the role comes from the token, not ?role=).
    service = qa_auth.service_headers()
    admin = qa_auth.role_token(base, "admin", "qa.smoke")
    alerts = "/api/v1/alerts/"
    created = (
        check(
            "M3 Alerts",
            "Create congestion alert (service key)",
            "POST",
            alerts,
            201,
            {
                "type": "congestion",
                "severity": "High",
                "road_id": "R002",
                "message": "QA Day 2 smoke: High congestion on R002.",
            },
            headers=service,
        )
        or {}
    )
    check(
        "M3 Alerts",
        "Create critical accident alert (service key)",
        "POST",
        alerts,
        201,
        {
            "type": "accident",
            "severity": "Critical",
            "road_id": "R003",
            "message": "QA Day 2 smoke: Critical accident on R003.",
        },
        headers=service,
    )
    check(
        "M3 Alerts",
        "Create without key/token rejected",
        "POST",
        alerts,
        401,
        {"type": "congestion", "severity": "High", "road_id": "R002", "message": "x"},
    )
    check(
        "M3 Alerts", "Missing fields rejected", "POST", alerts, 422, {"type": "x"}, headers=service
    )
    check("M3 Alerts", "List without token rejected", "GET", "/api/v1/alerts/my", 401)
    user_view = check(
        "M3 Alerts", "List as user (JWT)", "GET", "/api/v1/alerts/my", 200, token=access
    )
    admin_view = check(
        "M3 Alerts", "List as admin (JWT)", "GET", "/api/v1/alerts/my", 200, token=admin
    )
    user_view, admin_view = user_view or [], admin_view or []
    alert_id = created.get("alert_id")
    if alert_id is not None:
        check(
            "M3 Alerts", "Mark read", "PATCH", f"/api/v1/alerts/{alert_id}/read", 200, token=admin
        )
    check(
        "M3 Alerts",
        "Mark read unknown id -> 404",
        "PATCH",
        "/api/v1/alerts/99999999/read",
        404,
        token=admin,
    )

    # Role scoping from the JWT: public users don't see Critical or accident alerts.
    user_has_restricted = any(
        a.get("severity") == "Critical" or a.get("type") == "accident" for a in user_view
    )
    admin_has_critical = any(a.get("severity") == "Critical" for a in admin_view)
    results.append(
        (
            "M3 Alerts",
            "user view hides Critical + accident",
            "-",
            "(derived)",
            "True",
            str(not user_has_restricted),
            0.0,
            not user_has_restricted,
        )
    )
    results.append(
        (
            "M3 Alerts",
            "admin view includes Critical",
            "-",
            "(derived)",
            "True",
            str(admin_has_critical),
            0.0,
            admin_has_critical,
        )
    )

    # --- Report ---------------------------------------------------------
    print(f"Base URL: {base}\n")
    print("| Area | Check | Method | Path | Expected | Actual | ms | Result |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for area, name, method, path, expect, status, ms, ok in results:
        print(
            f"| {area} | {name} | {method} | `{path}` | {expect} | {status} | {ms:.0f} | "
            f"{'PASS' if ok else 'FAIL'} |"
        )
    failed = sum(1 for r in results if not r[-1])
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

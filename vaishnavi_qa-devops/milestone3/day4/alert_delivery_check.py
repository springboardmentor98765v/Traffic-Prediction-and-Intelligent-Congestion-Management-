"""Milestone 3 Day 4 — alert delivery timing + end-to-end producer checks.

TC-AL-25  create → visible latency over N alerts (p50/p95/max, lost count)
TC-AL-26  congestion watcher → live Alert API (trigger + dedup against the real service)
TC-AL-27  anomaly detector → accident alert

    python QA/milestone3/day4/alert_delivery_check.py [--base-url ...] [-n 50]
"""

import argparse
import json
import statistics
import sys
import time
import urllib.request
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "backend" / "backend" / "Intern_AI AND ML"))
sys.path.insert(0, str(REPO_ROOT / "QA" / "milestone3"))

import qa_auth  # noqa: E402

# Before importing the watcher: it reads ALERT_SERVICE_KEY at import time.
qa_auth.load_dev_env()
SERVICE = qa_auth.service_headers()
TOKENS = {}

from anomaly_detector import AnomalyDetector  # noqa: E402
from m3_day2_congestion_watcher import CongestionThresholdWatcher  # noqa: E402


def http(method, url, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status, json.loads(resp.read() or b"null")


def token(base, role):
    # Role comes from the JWT since the DEF-M3-005/012 fix, so read as a real account.
    if role not in TOKENS:
        TOKENS[role] = qa_auth.role_token(base, role, "qa.d4")
    return TOKENS[role]


def alerts_for(base, road, role="admin"):
    _, body = http(
        "GET", f"{base}/api/v1/alerts/my", headers={"Authorization": f"Bearer {token(base, role)}"}
    )
    return [a for a in body if a["road_id"] == road]


def latency(base, n):
    road = f"QA-LAT-{uuid.uuid4().hex[:6].upper()}"
    samples, lost = [], 0
    for i in range(n):
        t0 = time.perf_counter()
        _, created = http(
            "POST",
            f"{base}/api/v1/alerts/",
            headers=SERVICE,
            body={
                "type": "congestion",
                "severity": "High",
                "road_id": road,
                "message": f"latency probe {i}",
            },
        )
        while time.perf_counter() - t0 < 5:
            if any(a["alert_id"] == created["alert_id"] for a in alerts_for(base, road, "user")):
                samples.append((time.perf_counter() - t0) * 1000)
                break
        else:
            lost += 1
    samples.sort()
    p95 = samples[max(0, int(len(samples) * 0.95) - 1)] if samples else float("nan")
    return {
        "n": n,
        "delivered": len(samples),
        "lost": lost,
        "p50_ms": round(statistics.median(samples), 1) if samples else None,
        "p95_ms": round(p95, 1),
        "max_ms": round(max(samples), 1) if samples else None,
        "pass": lost == 0 and p95 < 1000,
    }


def watcher_e2e(base):
    road = f"QA-W-{uuid.uuid4().hex[:6].upper()}"
    w = CongestionThresholdWatcher(alert_api_url=f"{base}/api/v1/alerts/")
    reading = {
        "road_id": road,
        "vehicle_count": 90,
        "density": 18.0,
        "congestion_level": "High",
        "updated_at": "2026-09-24T09:00:00",
    }
    first = w.check_reading(reading)
    second = w.check_reading({**reading, "congestion_level": "Severe"})
    stored = alerts_for(base, road)
    return {
        "first_triggered": first["alert_triggered"],
        "second_reason": second.get("reason"),
        "stored_count": len(stored),
        "stored": stored[:1],
        "pass": first["alert_triggered"]
        and second.get("reason") == "alert_already_active"
        and len(stored) == 1,
    }


def accident_e2e(base):
    road = "R001"
    detector = AnomalyDetector()
    result = detector.analyze(road, "2026-09-22T08:00:00", 200, 3.0, 60.0)
    out = {
        "anomaly_class": result["anomaly_class"],
        "anomaly_score": round(float(result.get("anomaly_score", 0)), 3),
    }
    if result["anomaly_class"] != "possible_incident":
        out["pass"] = False
        return out
    before = {a["alert_id"] for a in alerts_for(base, road)}
    # Same payload shape automate_accident_alerts.py sends.
    status, created = http(
        "POST",
        f"{base}/api/v1/alerts/",
        headers=SERVICE,
        body={
            "type": "accident",
            "severity": "High",
            "road_id": road,
            "message": f"AI anomaly detector flagged a possible_incident on road {road}.",
        },
    )
    new = [a for a in alerts_for(base, road) if a["alert_id"] not in before]
    out.update(
        status=status,
        new_alerts=len(new),
        visible_to_user=any(
            a["alert_id"] == created["alert_id"] for a in alerts_for(base, road, "user")
        ),
    )
    out["pass"] = status == 201 and len(new) == 1 and new[0]["type"] == "accident"
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("-n", type=int, default=50)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    report = {
        "TC-AL-25 latency": latency(base, args.n),
        "TC-AL-26 watcher_e2e": watcher_e2e(base),
        "TC-AL-27 accident_e2e": accident_e2e(base),
    }
    print(json.dumps(report, indent=2, default=str))
    return 0 if all(r["pass"] for r in report.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

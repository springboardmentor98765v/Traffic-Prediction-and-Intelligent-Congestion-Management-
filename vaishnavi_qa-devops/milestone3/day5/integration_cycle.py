"""Milestone 3 Day 5 — full local integration cycle (M1 + M2 + M3), API level.

One journey across every service, as three real accounts (user / operator / admin):

  Auth → Monitoring → Prediction → Route Analysis → Analytics → AI Insights
       → Alerts (congestion watcher + anomaly detector producers) → RBAC-scoped visibility
       → frontend-facing contract (URLs the frontend actually calls, CORS)

Operator/admin accounts: public sign-up always creates role=user, so the script
promotes two fresh accounts in the dev DB (`docker exec ... psql UPDATE users`).

    docker compose -f docker-compose.dev.yml up -d
    bash QA/milestone3/day6/analytics_setup.sh
    python QA/milestone3/day5/integration_cycle.py

Uses 127.0.0.1, not localhost: on the QA machine `localhost` resolves to ::1 and
Docker Desktop's IPv6 port proxy resets ~45% of connections (DEF-M3-015).

Writes integration_results.md + integration_results.json next to this file
(or into M3_OUT_DIR).
Exit code 1 if any non-blocked check fails.
"""

import csv
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
# Results folder; Day 7 re-runs set M3_OUT_DIR so Day 5 evidence isn't overwritten.
OUT = Path(os.getenv("M3_OUT_DIR", HERE))
REPO_ROOT = HERE.parents[2]
BACKEND_DIR = REPO_ROOT / os.getenv("M3_BACKEND_DIR", "backend_updated/backend/Intern_AI AND ML")
# The frontend folder has been renamed during M3 (`Front end/` → `front-end/`);
# FRONTEND_DIR overrides, otherwise use whichever exists.
FRONTEND_DIR = REPO_ROOT / os.getenv(
    "FRONTEND_DIR",
    next(
        (
            d
            for d in (
                "Front-end(m-3) (1)/Front-end",
                "front-end/Front-end",
                "Front end/Front-end",
            )
            if (REPO_ROOT / d).is_dir()
        ),
        "Front-end(m-3) (1)/Front-end",
    ),
)
FRONTEND_API_JS = FRONTEND_DIR / "api.js"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))

from anomaly_detector import AnomalyDetector  # noqa: E402
from m3_day2_congestion_watcher import CongestionThresholdWatcher  # noqa: E402

GW = os.getenv("M3_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
AN = os.getenv("M3_ANALYTICS_URL", "http://127.0.0.1:8001").rstrip("/")
AI = os.getenv("M3_AI_URL", "http://127.0.0.1:8010").rstrip("/")
PG = "trafficvision-postgres-dev"
ORIGIN, DEST = "11.9416,79.8083", "11.9350,79.8100"
FRONTEND_ORIGIN = "http://127.0.0.1:5500"
ROADS = [f"R00{i}" for i in range(1, 7)]

results = []


def call(method, url, body=None, token=None, headers=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status, hdrs, payload = resp.status, resp.headers, resp.read()
    except urllib.error.HTTPError as exc:
        status, hdrs, payload = exc.code, exc.headers, exc.read()
    except OSError as exc:
        return None, {}, str(exc), (time.perf_counter() - t0) * 1000
    ms = (time.perf_counter() - t0) * 1000
    text = payload.decode(errors="replace")
    if raw:
        return status, hdrs, text, ms
    try:
        return status, hdrs, json.loads(text) if text else None, ms
    except ValueError:
        return status, hdrs, text, ms


def record(stage, check, expected, actual, ok, ms=None, ref="", blocked=False):
    verdict = "BLOCKED" if blocked else ("PASS" if ok else "FAIL")
    results.append(
        {
            "stage": stage,
            "check": check,
            "expected": str(expected),
            "actual": str(actual),
            "verdict": verdict,
            "ms": None if ms is None else round(ms),
            "ref": ref,
        }
    )
    return ok


def psql(sql):
    out = subprocess.run(
        ["docker", "exec", PG, "psql", "-U", "traffic", "-d", "trafficvision", "-tAc", sql],
        capture_output=True,
        text=True,
        check=False,
    )
    return out.stdout.strip()


# --- 1. Stack ------------------------------------------------------------


def stage_stack():
    s, _, _, ms = call("GET", GW + "/health")
    record("1 Stack", "Gateway /health", 200, s, s == 200, ms)
    s, _, _, ms = call("GET", AN + "/")
    record("1 Stack", "Analytics service /", 200, s, s == 200, ms)
    s, _, body, ms = call("GET", AI + "/health")
    record(
        "1 Stack",
        "AI Insights service :8010 reachable",
        "reachable",
        "connection refused" if s is None else s,
        s is not None,
        ms,
        "No AI Insights service in repo / compose",
        blocked=s is None,
    )


# --- 2. Auth + RBAC --------------------------------------------------------


def stage_auth():
    run = uuid.uuid4().hex[:8]
    accounts = {}
    for role in ("user", "operator", "admin"):
        email = f"qa.d5.{role}.{run}@gmail.com"
        creds = {"email": email, "password": "QaPass#2026"}
        s, _, _, ms = call(
            "POST", GW + "/api/v1/auth/register", {"name": f"qa_d5_{role}_{run}", **creds}
        )
        record("2 Auth", f"Register {role} account", 201, s, s == 201, ms)
        if role != "user":
            psql(f"UPDATE users SET role='{role}' WHERE email='{email}'")
        s, _, body, ms = call("POST", GW + "/api/v1/auth/login", creds)
        token = body.get("access_token") if isinstance(body, dict) else None
        record("2 Auth", f"Login {role}", 200, s, s == 200 and bool(token), ms)
        s, _, me, ms = call("GET", GW + "/api/v1/auth/me", token=token)
        want = "PUBLIC" if role == "user" else role.upper()
        got = me.get("role") if isinstance(me, dict) else me
        record("2 Auth", f"/me role for {role}", want, got, s == 200 and got == want, ms)
        accounts[role] = token
    s, _, _, ms = call("GET", GW + "/api/v1/auth/me")
    record("2 Auth", "/me without token rejected", 401, s, s == 401, ms)
    return accounts


# --- 3. Monitoring ---------------------------------------------------------


def stage_monitoring():
    s, _, live, ms = call("GET", GW + "/api/v1/traffic/live")
    roads = sorted(r["road_id"] for r in live) if s == 200 else []
    record("3 Monitoring", "Live traffic, 6 roads", ROADS, roads, roads == ROADS, ms)
    s, _, road, ms = call("GET", GW + "/api/v1/traffic/road/R001")
    record(
        "3 Monitoring",
        "Road R001 detail + history",
        200,
        s,
        s == 200 and bool(road.get("history")),
        ms,
    )
    s, _, _, ms = call("GET", GW + "/api/v1/traffic/density")
    record("3 Monitoring", "Density summary", 200, s, s == 200, ms)
    return {r["road_id"]: r for r in live} if s == 200 else {}


# --- 4. Prediction -------------------------------------------------------


def stage_prediction():
    ok_all, slowest = True, 0
    for road in ROADS:
        s, _, body, ms = call("GET", f"{GW}/api/v1/predict/congestion?road_id={road}")
        slowest = max(slowest, ms)
        ok_all &= s == 200 and body.get("predicted_level") in ("Low", "Medium", "High", "Severe")
    record(
        "4 Prediction",
        "Congestion prediction for all 6 roads",
        "200 + valid level",
        "all ok" if ok_all else "failure",
        ok_all,
        slowest,
    )
    s, _, _, ms = call("GET", GW + "/api/v1/predict/peak-hours?road_id=R001")
    record("4 Prediction", "Peak hours R001", 200, s, s == 200, ms)


# --- 5. Route analysis ---------------------------------------------------


def stage_route(token):
    q = f"origin={ORIGIN}&destination={DEST}"
    for ep, ref in (
        ("optimize", ""),
        ("alternate", "DEF-M3-004"),
        ("travel-time", ""),
        ("conditions", ""),
    ):
        s, _, body, ms = call("GET", f"{GW}/api/v1/route/{ep}?{q}", token=token)
        # DEF-M3-004 fix: with the maps API down, /alternate may answer 503 with a message.
        ok = s == 200 or (
            ep == "alternate" and s == 503 and isinstance(body, dict) and body.get("detail")
        )
        record(
            "5 Route",
            f"/route/{ep} (logged-in user)",
            "200 (alternate: 200 or 503 + detail)" if ep == "alternate" else 200,
            s,
            bool(ok),
            ms,
            ref if not ok else "",
        )
    s, _, _, ms = call("GET", f"{GW}/api/v1/route/optimize?{q}")
    record("5 Route", "/route/optimize without token rejected", 401, s, s == 401, ms)


# --- 6. Analytics (cross-service consistency with Monitoring) ------------


def stage_analytics(live):
    s, _, trends, ms = call("GET", AN + "/analytics/trends?road_id=R001")
    record(
        "6 Analytics",
        "Trends R001 (4 weeks)",
        "200, 28 days",
        f"{s}, {len(trends.get('daily_trends', [])) if s == 200 else '-'} days",
        s == 200 and len(trends["daily_trends"]) == 28,
        ms,
    )
    s, _, heat, ms = call("GET", AN + "/analytics/heatmap?time_bucket=hour")
    heat_roads = heat.get("roads") if s == 200 else []
    record(
        "6 Analytics",
        "Heatmap roads == Monitoring roads",
        sorted(live),
        heat_roads,
        sorted(live) == heat_roads,
        ms,
    )
    s, hdrs, text, ms = call("GET", AN + "/analytics/reports?road_id=R001&limit=50000", raw=True)
    rows = list(csv.DictReader(io.StringIO(text))) if s == 200 else []
    record("6 Analytics", "Report CSV R001", 200, s, s == 200 and len(rows) > 0, ms)
    # Latest Monitoring reading must be the same DB row Analytics reports.
    # Monitoring returns naive IST wall-clock time; the report returns UTC with offset.
    latest = live.get("R001", {})
    ts = latest.get("updated_at", "")
    record(
        "6 Analytics",
        "Monitoring `updated_at` carries a timezone",
        "offset or Z",
        ts,
        ts.endswith("Z") or "+" in ts[10:],
        ref="DEF-M3-016" if "+" not in ts[10:] else "",
    )
    want = datetime.fromisoformat(ts).replace(tzinfo=ZoneInfo("Asia/Kolkata")) if ts else None
    match = [r for r in rows if want and datetime.fromisoformat(r["reading_timestamp"]) == want]
    got = match[0]["vehicle_count"] if match else "not found"
    record(
        "6 Analytics",
        f"Monitoring latest R001 ({ts} IST) == Analytics report row",
        latest.get("vehicle_count"),
        got,
        bool(match) and int(got) == latest.get("vehicle_count"),
    )


# --- 7. AI Insights -------------------------------------------------------


def stage_ai():
    s, _, body, ms = call("GET", AI + "/api/v1/ai/recommendations?road_id=R001")
    record(
        "7 AI Insights",
        "GET :8010/api/v1/ai/recommendations?road_id=R001 (frontend URL)",
        "200 {road_id, recommendation_text, based_on}",
        "connection refused" if s is None else s,
        s == 200,
        ms,
        "TC-AI-01; no service",
        blocked=s is None,
    )
    detector = AnomalyDetector()
    base = detector.analyze("R001", "2026-08-18T08:00:00", 91, 27.0, 18.3)
    record(
        "7 AI Insights",
        "Anomaly detector: baseline-like R001 reading",
        "normal",
        base["anomaly_class"],
        base["anomaly_class"] == "normal",
    )


# --- 8. Alerts: producers end-to-end -------------------------------------


def my_alerts(token=None, role=None):
    path = "/api/v1/alerts/my" + (f"?role={role}" if role else "")
    s, _, body, _ = call("GET", GW + path, token=token)
    return s, (body if isinstance(body, list) else [])


def stage_alert_producers(tokens):
    # 8a. Replay 4 weeks of real R003 readings (from the Analytics report) through
    # the congestion watcher. Readings are re-labelled to a QA road id so the
    # real R003 alert feed isn't flooded; the congestion levels are real.
    s, _, text, _ = call("GET", AN + "/analytics/reports?road_id=R003&limit=50000", raw=True)
    rows = sorted(csv.DictReader(io.StringIO(text)), key=lambda r: r["reading_timestamp"])
    qa_road = f"QA-D5-R003-{uuid.uuid4().hex[:4].upper()}"
    watcher = CongestionThresholdWatcher(alert_api_url=GW + "/api/v1/alerts/")
    expected_edges, prev_hot = 0, False
    for r in rows:
        hot = r["congestion_level"] in ("High", "Severe")
        expected_edges += hot and not prev_hot
        prev_hot = hot
        watcher.check_reading(
            {
                "road_id": qa_road,
                "vehicle_count": int(r["vehicle_count"]),
                "density": float(r["traffic_density_vehicles_per_km"]),
                "congestion_level": r["congestion_level"],
                "updated_at": r["reading_timestamp"],
            }
        )
    stored = [a for a in my_alerts(tokens["admin"], "admin")[1] if a["road_id"] == qa_road]
    record(
        "8 Alerts E2E",
        f"Watcher replay of {len(rows)} real R003 readings → alerts",
        f"{expected_edges} (one per High/Severe episode)",
        len(stored),
        len(stored) == expected_edges and expected_edges > 0,
        ref="" if len(stored) == expected_edges and expected_edges > 0 else "DEF-M3-025",
    )

    # 8b. Anomaly detector → accident alert, as automate_accident_alerts.py does it.
    detector = AnomalyDetector()
    res = detector.analyze("R004", "2026-08-18T08:00:00", 200, 3.0, 60.0)
    payload = {
        "type": "accident",
        "severity": "High",
        "road_id": "R004",
        "message": "AI anomaly detector flagged a possible_incident on road R004.",
    }
    # As shipped, automate_accident_alerts.py posts with no credentials.
    s, _, _, _ = call("POST", GW + "/api/v1/alerts/", payload)
    record(
        "8 Alerts E2E",
        "Accident producer posts as shipped (no credentials)",
        201,
        s,
        s == 201,
        ref="" if s == 201 else "DEF-M3-025",
    )
    # Setup for the visibility checks below: create it with an admin JWT.
    t0 = time.perf_counter()
    s, _, created, _ = call("POST", GW + "/api/v1/alerts/", payload, token=tokens["admin"])
    accident_id = created.get("alert_id") if isinstance(created, dict) else None
    seen_ms = None
    while time.perf_counter() - t0 < 5:
        if any(a["alert_id"] == accident_id for a in my_alerts(tokens["operator"])[1]):
            seen_ms = (time.perf_counter() - t0) * 1000
            break
    record(
        "8 Alerts E2E",
        "Incident reading R004 → detector class",
        "possible_incident",
        res["anomaly_class"],
        res["anomaly_class"] == "possible_incident",
    )
    record(
        "8 Alerts E2E",
        "Accident alert stored and visible to operator (frontend call)",
        "visible < 2 s",
        f"{round(seen_ms)} ms" if seen_ms else "not visible",
        seen_ms is not None and seen_ms < 2000,
        seen_ms,
    )

    # 8c. A Critical accident alert, the severity the SRS reserves for operator/admin.
    s, _, crit, _ = call(
        "POST",
        GW + "/api/v1/alerts/",
        {
            "type": "accident",
            "severity": "Critical",
            "road_id": "R004",
            "message": "QA Day 5: multi-vehicle collision, lanes blocked on R004.",
        },
        token=tokens["admin"],
    )
    return accident_id, crit.get("alert_id") if isinstance(crit, dict) else None


# --- 9. RBAC-scoped alert visibility --------------------------------------


def stage_alert_rbac(tokens, accident_id, critical_id):
    def visible(alert_id, token=None, role=None):
        s, alerts = my_alerts(token, role)
        return s, any(a["alert_id"] == alert_id for a in alerts)

    # The frontend (api.js alertsAPI.getMyAlerts) calls GET /alerts/my with the JWT
    # and no ?role=, so these rows are what each dashboard actually shows.
    for role, want in (("user", False), ("operator", True), ("admin", True)):
        s, vis = visible(critical_id, tokens[role])
        ref = "" if vis == want else ("DEF-M3-012" if role != "user" else "DEF-M3-024")
        record(
            "9 Alert RBAC",
            f"Critical alert visible to {role} (frontend call, JWT only)",
            want,
            vis,
            s == 200 and vis == want,
            ref=ref,
        )
    s, vis = visible(accident_id, tokens["user"])
    record(
        "9 Alert RBAC",
        "Accident alert (High, from detector) hidden from public user",
        False,
        vis,
        not vis,
        ref="" if not vis else "DEF-M3-007",
    )
    s, vis = visible(critical_id, tokens["user"], role="admin")
    record(
        "9 Alert RBAC",
        "Public user JWT + ?role=admin cannot see Critical",
        False,
        vis,
        not vis,
        ref="" if not vis else "DEF-M3-005",
    )
    s, _ = my_alerts(None)
    record(
        "9 Alert RBAC",
        "GET /alerts/my without token rejected",
        401,
        s,
        s == 401,
        ref="" if s == 401 else "DEF-M3-005",
    )
    s, _, _, _ = call(
        "POST",
        GW + "/api/v1/alerts/",
        {
            "type": "accident",
            "severity": "Critical",
            "road_id": "QA-D5-FORGED",
            "message": "forged",
        },
    )
    record(
        "9 Alert RBAC",
        "POST /alerts/ without token rejected",
        "401/403",
        s,
        s in (401, 403),
        ref="" if s in (401, 403) else "DEF-M3-005",
    )
    s, _, _, _ = call(
        "POST",
        GW + "/api/v1/alerts/",
        {"type": "accident", "severity": "Critical", "road_id": "QA-D5-FORGED", "message": "x"},
        token=tokens["user"],
    )
    record(
        "9 Alert RBAC",
        "Public user JWT cannot create alerts",
        "403",
        s,
        s == 403,
        ref="" if s == 403 else "DEF-M3-005",
    )
    s, _, _, _ = call("PATCH", f"{GW}/api/v1/alerts/{critical_id}/read", token=tokens["user"])
    record(
        "9 Alert RBAC",
        "Public user can't mark a Critical alert read",
        "403/404",
        s,
        s in (403, 404),
        ref="" if s in (403, 404) else "DEF-M3-005",
    )


# --- 10. Frontend-facing contract -----------------------------------------


def stage_frontend_contract():
    src = FRONTEND_API_JS.read_text(encoding="utf-8")

    def cfg(key):
        marker = f"{key}: '"
        i = src.index(marker) + len(marker)
        return src[i : src.index("'", i)]

    an_base = cfg("ANALYTICS_BASE")
    s, _, _, ms = call("GET", an_base + "/analytics/heatmap?time_bucket=hour")
    record(
        "10 Frontend contract",
        f"api.js ANALYTICS_BASE ({an_base}) serves /analytics/heatmap",
        200,
        s,
        s == 200,
        ms,
        "" if s == 200 else "DEF-M3-013",
    )
    for name, url in (
        ("Gateway", GW + "/api/v1/traffic/live"),
        ("Analytics", AN + "/analytics/trends?road_id=R001"),
    ):
        s, hdrs, _, _ = call("GET", url, headers={"Origin": FRONTEND_ORIGIN})
        acao = hdrs.get("access-control-allow-origin") if hdrs else None
        record(
            "10 Frontend contract",
            f"{name} sends CORS header to browser origin",
            "Access-Control-Allow-Origin",
            acao or "missing",
            bool(acao),
            ref="" if acao else "DEF-M3-014",
        )


def write_reports():
    counts = {v: sum(r["verdict"] == v for r in results) for v in ("PASS", "FAIL", "BLOCKED")}
    (OUT / "integration_results.json").write_text(
        json.dumps({"summary": counts, "results": results}, indent=2), encoding="utf-8"
    )
    lines = [
        "# Milestone 3 Day 5 — Integration Cycle Results (API level)",
        "",
        f"Executed {time.strftime('%Y-%m-%d %H:%M')} · "
        "`python QA/milestone3/day5/integration_cycle.py`"
        f" · gateway {GW} · analytics {AN} · AI {AI}",
        "",
        f"**{counts['PASS']} pass · {counts['FAIL']} fail · {counts['BLOCKED']} blocked**"
        f" (of {len(results)})",
        "",
        "| Stage | Check | Expected | Actual | ms | Result | Ref |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        lines.append(
            f"| {r['stage']} | {r['check']} | {r['expected']} | {r['actual']} | "
            f"{'' if r['ms'] is None else r['ms']} | {r['verdict']} | {r['ref']} |"
        )
    (OUT / "integration_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return counts


def main():
    stage_stack()
    tokens = stage_auth()
    live = stage_monitoring()
    stage_prediction()
    stage_route(tokens["user"])
    stage_analytics(live)
    stage_ai()
    accident_id, critical_id = stage_alert_producers(tokens)
    stage_alert_rbac(tokens, accident_id, critical_id)
    stage_frontend_contract()
    counts = write_reports()
    for r in results:
        print(f"{r['verdict']:7} {r['stage']:22} {r['check']}  -> {r['actual']} {r['ref']}")
    print(counts)
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

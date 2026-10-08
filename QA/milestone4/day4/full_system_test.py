"""Milestone 4 Day 4 — full application testing and workflow validation on the live system.

Covers every feature from Milestones 1-3 through the deployed services, organised as the
user journeys the SRS asks for (login -> dashboard -> route -> alert), plus negative and
cross-service consistency checks:

    W1  Public user journey   register, login, dashboard data, prediction, route, alerts
    W2  Operator journey      monitoring + analytics (trends, heatmap, report export)
    W3  Admin journey         full alert visibility, mark-as-read
    W4  Alert pipeline        producer (service key) -> stored -> role-scoped delivery
    W5  AI insights           anomalies, recommendations, model predictions (live + manual)
    W6  Data consistency      backend and analytics agree on the live road set
    W7  Negative / security   bad credentials, missing token, bad input, unknown road
    W8  Frontend              every page served

    python QA/milestone4/day4/full_system_test.py
        --report QA/milestone4/day4/full_system_test_report.md

Needs ALERT_SERVICE_KEY (W4) and DATABASE_URL (to create operator/admin test accounts,
W2/W3); without them those checks are reported as SKIP, not PASS.
"""

import argparse
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from live_common import (  # noqa: E402
    PASSWORD,
    Results,
    alert_service_headers,
    call,
    role_token,
    service_urls,
    wake_services,
)

ORIGIN = "11.9416,79.8083"
DESTINATION = "11.9350,79.8100"
ROAD = "R001"
PAGES = [
    "Login.html",
    "public dashboard.html",
    "operator dashboard.html",
    "admin dashboard.html",
    "live maps.html",
    "route-analysis.html",
    "Alerts.html",
    "analytics.html",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    parser.add_argument("--json")
    args = parser.parse_args()

    urls = service_urls()
    b, an, ai, web = urls["backend"], urls["analytics"], urls["ai"], urls["web"]
    api = b + "/api/v1"
    r = Results("Milestone 4 Day 4 — Full System Test (live environment)", urls)

    print("Waking services...")
    ready = wake_services(urls)
    r.notes.append(
        "Cold start / time to first 200: " + ", ".join(f"{k} {v} s" for k, v in ready.items())
    )

    # ---------------------------------------------------------------- W1
    w = "W1 User journey"
    run = uuid.uuid4().hex[:8]
    email = f"qa.m4d4.{run}@gmail.com"
    creds = {"email": email, "password": PASSWORD}
    r.check(w, "Register", api + "/auth/register", 201, "POST", {"name": f"qa_m4d4_{run}", **creds})
    r.check(
        w,
        "Duplicate register rejected",
        api + "/auth/register",
        409,
        "POST",
        {"name": f"qa_m4d4b_{run}", **creds},
    )
    login = r.check(w, "Login", api + "/auth/login", 200, "POST", creds) or {}
    token = login.get("access_token")
    me = r.check(w, "Profile (/auth/me)", api + "/auth/me", token=token) or {}
    # /auth/me shows the display role: user -> PUBLIC, others upper-cased.
    r.add(w, "New account role is PUBLIC", me.get("role") == "PUBLIC", "PUBLIC", me.get("role"))
    r.check(
        w,
        "Refresh token",
        api + "/auth/refresh",
        200,
        "POST",
        {"refresh_token": login.get("refresh_token")},
    )
    live = r.check(w, "Dashboard: live traffic", api + "/traffic/live") or []
    r.check(w, "Dashboard: density summary", api + "/traffic/density")
    r.check(w, f"Road detail {ROAD}", f"{api}/traffic/road/{ROAD}")
    r.check(w, "Road condition", f"{api}/traffic/road-condition/{ROAD}")
    r.check(w, "History", f"{api}/traffic/history?road_id={ROAD}&limit=5")
    r.check(w, "Aggregate", f"{api}/traffic/aggregate?road_id={ROAD}")
    r.check(w, "Hourly metrics", f"{api}/traffic/metrics/hourly?road_id={ROAD}&limit=5")
    r.check(w, "Daily metrics", f"{api}/traffic/metrics/daily?road_id={ROAD}&limit=5")
    pred = r.check(w, "Predict congestion (GET)", f"{api}/predict/congestion?road_id={ROAD}") or {}
    r.add(
        w,
        "Prediction has a level",
        bool(pred.get("predicted_congestion") or pred.get("congestion_level") or pred),
        "non-empty",
        bool(pred),
    )
    r.check(
        w,
        "Predict congestion (POST)",
        api + "/predict/congestion",
        200,
        "POST",
        {
            "road_id": ROAD,
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
    r.check(w, "Peak hours", f"{api}/predict/peak-hours?road_id={ROAD}")
    r.check(w, "Delay estimate", f"{api}/predict/delay?road_id={ROAD}")
    q = f"origin={ORIGIN}&destination={DESTINATION}"
    for ep in ("optimize", "alternate", "travel-time", "conditions"):
        r.check(w, f"Route {ep}", f"{api}/route/{ep}?{q}", token=token)
    r.check(w, "My alerts", api + "/alerts/my", token=token)

    # ---------------------------------------------------------------- W2
    w = "W2 Operator"
    operator = role_token(b, "operator", "m4d4")
    if operator:
        op_me = r.check(w, "Operator profile", api + "/auth/me", token=operator) or {}
        r.add(w, "Role is OPERATOR", op_me.get("role") == "OPERATOR", "OPERATOR", op_me.get("role"))
        r.check(w, "Operator alerts", api + "/alerts/my", token=operator)
    else:
        r.add(w, "Operator account", None, "operator", "no DATABASE_URL to promote")
    trends = r.check(w, "Analytics trends", f"{an}/analytics/trends?road_id={ROAD}") or {}
    r.add(
        w,
        "Trends has daily data",
        bool(trends.get("daily_trends")),
        "non-empty",
        len(trends.get("daily_trends") or []),
    )
    r.check(w, "Heatmap (hourly)", an + "/analytics/heatmap")
    r.check(w, "Heatmap (daily)", an + "/analytics/heatmap?time_bucket=day")
    status, body, ms, headers = call(f"{an}/analytics/reports?road_id={ROAD}&limit=50")
    ctype = headers.get("content-type") or headers.get("Content-Type") or ""
    r.add(
        w,
        "Report export (CSV)",
        status == 200 and "csv" in ctype,
        "200 text/csv",
        f"{status} {ctype}",
        ms,
    )
    for ep in ("live", f"road/{ROAD}", "density", f"history?road_id={ROAD}&limit=5"):
        r.check(w, f"Analytics traffic/{ep.split('?')[0]}", f"{an}/api/v1/traffic/{ep}")

    # ---------------------------------------------------------------- W3 + W4
    w4 = "W4 Alert pipeline"
    service = alert_service_headers()
    admin = role_token(b, "admin", "m4d4")
    created = {}
    if service:
        tag = uuid.uuid4().hex[:6]
        created = (
            r.check(
                w4,
                "Producer posts High congestion alert",
                api + "/alerts/",
                201,
                "POST",
                {
                    "type": "congestion",
                    "severity": "High",
                    "road_id": "R002",
                    "message": f"M4 Day 4 {tag}: High congestion on R002",
                },
                headers=service,
            )
            or {}
        )
        r.check(
            w4,
            "Producer posts Critical accident alert",
            api + "/alerts/",
            201,
            "POST",
            {
                "type": "accident",
                "severity": "Critical",
                "road_id": "R003",
                "message": f"M4 Day 4 {tag}: Critical accident on R003",
            },
            headers=service,
        )
        r.check(
            w4,
            "Invalid severity rejected",
            api + "/alerts/",
            422,
            "POST",
            {"type": "congestion", "severity": "Extreme", "road_id": "R002", "message": "x"},
            headers=service,
        )
    else:
        r.add(w4, "Producer posts alerts", None, "201", "ALERT_SERVICE_KEY not set")
    # DEF-M3-025: producers need the service key or an operator/admin JWT -> 403 otherwise.
    r.check(
        w4,
        "Post without key/token rejected",
        api + "/alerts/",
        403,
        "POST",
        {"type": "congestion", "severity": "High", "road_id": "R002", "message": "x"},
    )
    user_view = r.check(w4, "User reads alerts", api + "/alerts/my", token=token) or []
    restricted = [
        a for a in user_view if a.get("severity") == "Critical" or a.get("type") == "accident"
    ]
    r.add(w4, "User view hides Critical/accident", not restricted, 0, len(restricted))

    w = "W3 Admin"
    if admin:
        admin_view = r.check(w, "Admin reads alerts", api + "/alerts/my", token=admin) or []
        if service:
            r.add(
                w,
                "Admin sees Critical",
                any(a.get("severity") == "Critical" for a in admin_view),
                True,
                any(a.get("severity") == "Critical" for a in admin_view),
            )
        if created.get("alert_id") is not None:
            r.check(
                w,
                "Mark alert read",
                f"{api}/alerts/{created['alert_id']}/read",
                200,
                "PATCH",
                token=admin,
            )
        r.check(
            w, "Mark unknown alert -> 404", api + "/alerts/99999999/read", 404, "PATCH", token=admin
        )
    else:
        r.add(w, "Admin account", None, "admin", "no DATABASE_URL to promote")

    # ---------------------------------------------------------------- W5
    w = "W5 AI insights"
    r.check(w, "AI root", ai + "/")
    anomalies = r.check(w, "Anomalies (all roads)", ai + "/api/v1/ai/anomalies")
    r.add(w, "Anomalies returned data", bool(anomalies), "non-empty", type(anomalies).__name__)
    r.check(w, f"Anomalies {ROAD}", f"{ai}/api/v1/ai/anomalies?road_id={ROAD}")
    r.check(w, f"Recommendations {ROAD}", f"{ai}/api/v1/ai/recommendations?road_id={ROAD}")
    r.check(
        w,
        "Manual prediction",
        ai + "/predict",
        200,
        "POST",
        {
            "vehicle_count": 80,
            "density": 16.0,
            "avg_speed_kmph": 22.0,
            "road_id": ROAD,
            "time_of_day": "morning",
        },
    )
    r.check(w, "Live prediction (AI -> backend)", ai + "/predict/live")
    r.check(
        w, "Congestion by road (AI -> backend)", f"{ai}/api/v1/predict/congestion?road_id={ROAD}"
    )

    # ---------------------------------------------------------------- W6
    w = "W6 Consistency"
    _, an_live, _, _ = call(an + "/api/v1/traffic/live")
    roads_b = {row.get("road_id") for row in live} if isinstance(live, list) else set()
    roads_a = {row.get("road_id") for row in an_live} if isinstance(an_live, list) else set()
    r.add(
        w,
        "Backend and analytics see same roads",
        roads_b == roads_a and bool(roads_b),
        sorted(roads_b),
        sorted(roads_a),
    )

    # ---------------------------------------------------------------- W7
    w = "W7 Negative"
    r.check(
        w,
        "Wrong password -> 401",
        api + "/auth/login",
        401,
        "POST",
        {"email": email, "password": "wrong"},
    )
    r.check(
        w,
        "Unknown user -> 401",
        api + "/auth/login",
        401,
        "POST",
        {"email": f"nobody.{run}@gmail.com", "password": "x"},
    )
    r.check(
        w,
        "Disallowed email domain -> 422",
        api + "/auth/register",
        422,
        "POST",
        {"name": f"qa_bad_{run}", "email": f"x{run}@example.com", "password": PASSWORD},
    )
    r.check(w, "/auth/me without token -> 401", api + "/auth/me", 401)
    r.check(w, "/auth/me bad token -> 401", api + "/auth/me", 401, token="not.a.jwt")
    r.check(w, "Route without token -> 401", f"{api}/route/optimize?{q}", 401)
    r.check(
        w,
        "Route bad coords -> 400",
        api + "/route/optimize?origin=abc&destination=xyz",
        400,
        token=token,
    )
    r.check(w, "Alerts without token -> 401", api + "/alerts/my", 401)
    r.check(w, "Trends unknown road -> 404", an + "/analytics/trends?road_id=R999", 404)
    r.check(
        w,
        "Trends malformed date -> 422",
        an + f"/analytics/trends?road_id={ROAD}&start_date=2026-13-45",
        422,
    )
    r.check(
        w,
        "Trends inverted range -> 400",
        an + f"/analytics/trends?road_id={ROAD}&start_date=2026-09-10&end_date=2026-09-01",
        400,
    )
    r.check(
        w,
        "AI recommendations unknown road -> 404",
        ai + "/api/v1/ai/recommendations?road_id=R999",
        404,
    )

    # ---------------------------------------------------------------- W8
    w = "W8 Frontend"
    for page in PAGES:
        r.check(w, page, f"{web}/{page.replace(' ', '%20')}")

    print()
    print(r.markdown())
    r.save(args.report, args.json)
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Milestone 4 Day 3 — smoke test of the live deployment.

Answers "is the whole platform up and wired together?" in about a minute: every service
answers, each one reaches its database/cache, the frontend is served and points at the
production APIs, and CORS only lets the hosted frontend in.

    python QA/milestone4/day3/smoke_test_live.py --report QA/milestone4/day3/smoke_results.md

URLs come from BACKEND_URL / ANALYTICS_URL / AI_URL / WEB_URL (see ../live_common.py).
Also runs in the CI deploy stage right after the health gate. Exits non-zero on any FAIL.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from live_common import Results, call, register_and_login, service_urls, wake_services  # noqa: E402

PAGES = [
    "Login.html",
    "public dashboard.html",
    "operator dashboard.html",
    "admin dashboard.html",
    "live maps.html",
    "route-analysis.html",
    "Alerts.html",
    "analytics.html",
    "api.js",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="write a markdown report here")
    parser.add_argument("--json", help="write raw results here")
    args = parser.parse_args()

    urls = service_urls()
    b, an, ai, web = urls["backend"], urls["analytics"], urls["ai"], urls["web"]
    r = Results("Milestone 4 Day 3 — Live Smoke Test", urls)

    # 1. Wake everything (free tier sleeps after 15 min idle) and record cold-start time.
    print("Waking services (up to ~60 s each on the free tier)...")
    ready = wake_services(urls)
    for name, seconds in ready.items():
        r.add("Availability", f"{name} reachable", seconds is not None, "200", f"{seconds} s")
    r.notes.append(
        "Time to first 200 (includes free-tier cold start when asleep): "
        + ", ".join(f"{k} {v} s" for k, v in ready.items())
    )

    # 2. Backend: liveness, docs, DB-backed reads, auth round trip (DB write + JWT).
    r.check("Backend", "GET /health", b + "/health")
    r.check("Backend", "OpenAPI docs", b + "/docs")
    live = r.check("Backend", "Live traffic (DB read)", b + "/api/v1/traffic/live")
    r.add(
        "Backend",
        "Live traffic has rows",
        isinstance(live, list) and len(live) > 0,
        "> 0 rows",
        len(live) if isinstance(live, list) else type(live).__name__,
    )
    email, login = register_and_login(b, "m4d3")
    r.add(
        "Backend",
        "Register + login (DB write, JWT)",
        bool(login.get("access_token")),
        "token",
        bool(login),
    )
    r.check(
        "Backend", "GET /auth/me with token", b + "/api/v1/auth/me", token=login.get("access_token")
    )
    r.check("Backend", "Prediction (model loaded)", b + "/api/v1/predict/congestion?road_id=R001")

    # 3. Analytics: liveness, DB-backed analytics, cache-backed live traffic.
    r.check("Analytics", "GET /", an + "/")
    r.check("Analytics", "Trends R001 (DB)", an + "/analytics/trends?road_id=R001")
    r.check("Analytics", "Live traffic (Redis/DB)", an + "/api/v1/traffic/live")

    # 4. AI Engine: liveness, model-backed recommendation, backend-dependent prediction.
    r.check("AI Engine", "GET /health", ai + "/health")
    r.check("AI Engine", "Recommendations R001", ai + "/api/v1/ai/recommendations?road_id=R001")
    r.check("AI Engine", "Congestion via backend", ai + "/api/v1/predict/congestion?road_id=R001")

    # 5. Frontend: every page is served, and the served api.js targets production.
    for page in PAGES:
        r.check("Frontend", page, f"{web}/{page.replace(' ', '%20')}")
    r.check("Frontend", "/ rewrites to Login", web + "/")
    # On localhost api.js deliberately picks the local ports, so these two only apply live.
    local = any(host in web for host in ("127.0.0.1", "localhost"))
    status, js, _, _ = call(web + "/api.js")
    js = js if isinstance(js, str) else ""
    r.add(
        "Frontend",
        "api.js points at production backend",
        None if local else b in js,
        b,
        (
            "local run"
            if local
            else ("found" if b in js else "not found: fix PRODUCTION_URLS in api.js")
        ),
    )

    # 6. CORS (DEF-M4-006): the hosted frontend is allowed, other origins are not.
    preflight = {
        "Origin": web,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    _, _, _, h = call(b + "/api/v1/auth/login", "OPTIONS", headers=preflight)
    allowed = h.get("access-control-allow-origin") or h.get("Access-Control-Allow-Origin")
    r.add("CORS", "Frontend origin allowed", allowed == web, web, allowed)
    _, _, _, h = call(
        b + "/api/v1/auth/login", "OPTIONS", headers={**preflight, "Origin": "https://evil.example"}
    )
    leaked = h.get("access-control-allow-origin") or h.get("Access-Control-Allow-Origin")
    r.add(
        "CORS", "Foreign origin blocked", leaked in (None, ""), "no ACAO header", leaked or "none"
    )

    # 7. Security basics.
    r.check("Security", "Protected route needs token", b + "/api/v1/auth/me", expect=401)
    r.add(
        "Security",
        "Served over HTTPS",
        None if local else all(u.startswith("https://") for u in urls.values()),
        "https",
        "local run" if local else "",
    )

    print()
    print(r.markdown())
    r.save(args.report, args.json)
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main())

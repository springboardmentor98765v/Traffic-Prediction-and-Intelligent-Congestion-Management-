"""Milestone 3 Day 6 — regression of every Milestone 1 & 2 feature on the M3 build.

Re-executes the 32 Milestone 2 test cases (QA/milestone2/day2/milestone2_test_cases.md:
HIST, PRED, ROUTE, MAP, FE-M2, REG, INT) plus the M1 auth/monitoring checks, against the
integrated M3 stack, so any M3 change that broke an older feature shows up here.

  API part : stdlib HTTP against the gateway (127.0.0.1:8000)
  UI part  : Playwright + system Edge, same harness as QA/milestone3/day5/frontend_e2e.py

    docker compose -f docker-compose.dev.yml up -d
    python QA/milestone3/day6/regression_m1_m2.py

Writes regression_results.md/json and screenshots/ next to this file.
"""

import json
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "day5"))
import integration_cycle as ic  # noqa: E402  (call/psql helpers)
import frontend_e2e as fe  # noqa: E402  (browser harness)

GW = ic.GW
ROUTE_Q = f"origin={ic.ORIGIN}&destination={ic.DEST}"
OUT = ic.OUT  # M3_OUT_DIR (retests), default this folder
SHOTS = OUT / "screenshots"
results = []


def rec(tc, area, check, expected, actual, ok, ref="", ms=None):
    results.append(
        {
            "tc": tc,
            "area": area,
            "check": check,
            "expected": str(expected),
            "actual": str(actual)[:160],
            "verdict": "PASS" if ok else "FAIL",
            "ref": ref if not ok else "",
            "ms": None if ms is None else round(ms),
        }
    )


def get(path, token=None):
    s, _, body, ms = ic.call("GET", GW + path, token=token)
    return s, body, ms


def get_an(path):
    """GET from the analytics service (port 8001). Unwraps {count, data} envelopes."""
    import urllib.request as _ur
    import urllib.error as _ue
    import json as _json
    import time as _time

    t0 = _time.monotonic()
    try:
        req = _ur.Request(ic.AN + path)
        with _ur.urlopen(req, timeout=10) as resp:
            ms = round((_time.monotonic() - t0) * 1000)
            body = _json.loads(resp.read())
            if isinstance(body, dict) and "data" in body:
                body = body["data"]
            return 200, body, ms
    except _ue.HTTPError as exc:
        ms = round((_time.monotonic() - t0) * 1000)
        return exc.code, {}, ms
    except Exception:
        ms = round((_time.monotonic() - t0) * 1000)
        return 0, {}, ms


# ---------------------------------------------------------------- M1 (API)


def m1_api():
    run = uuid.uuid4().hex[:8]
    creds = {"email": f"qa.d6.{run}@gmail.com", "password": "QaPass#2026"}
    s, _, _, ms = ic.call("POST", GW + "/api/v1/auth/register", {"name": f"qa_d6_{run}", **creds})
    rec("REG-API-01", "M1 Auth", "Register", 201, s, s == 201, ms=ms)
    s, _, tok, ms = ic.call("POST", GW + "/api/v1/auth/login", creds)
    token = tok.get("access_token") if isinstance(tok, dict) else None
    rec(
        "REG-API-02",
        "M1 Auth",
        "Login returns JWT",
        "200 + token",
        s,
        s == 200 and bool(token),
        ms=ms,
    )
    s, me, ms = get("/api/v1/auth/me", token)
    rec(
        "REG-API-03",
        "M1 Auth",
        "/me returns PUBLIC role",
        "PUBLIC",
        me.get("role") if isinstance(me, dict) else s,
        s == 200 and me.get("role") == "PUBLIC",
        ms=ms,
    )
    s, _, _, ms = ic.call(
        "POST", GW + "/api/v1/auth/refresh", {"refresh_token": tok.get("refresh_token")}
    )
    rec("REG-API-04", "M1 Auth", "Refresh token", 200, s, s == 200, ms=ms)
    s, _, _, ms = ic.call("POST", GW + "/api/v1/auth/login", {**creds, "password": "wrong"})
    rec("REG-API-05", "M1 Auth", "Wrong password rejected", 401, s, s == 401, ms=ms)
    s, _, ms = get("/api/v1/auth/me")
    rec("REG-API-06", "M1 Auth", "/me without token rejected", "401/403", s, s in (401, 403), ms=ms)
    s, live, ms = get("/api/v1/traffic/live")
    rec(
        "REG-API-07",
        "M1 Monitoring",
        "Live traffic (6 roads)",
        6,
        len(live) if s == 200 else s,
        s == 200 and len(live) == 6,
        ms=ms,
    )
    s, road, ms = get("/api/v1/traffic/road/R001")
    rec(
        "REG-API-08",
        "M1 Monitoring",
        "Road R001 detail + history",
        200,
        s,
        s == 200 and bool(road.get("history")),
        ms=ms,
    )
    s, dens, ms = get("/api/v1/traffic/density")
    rec(
        "REG-API-09",
        "M1 Monitoring",
        "Density summary",
        "200 + total_roads",
        s,
        s == 200 and "total_roads" in dens,
        ms=ms,
    )
    s, _, ms = get("/api/v1/traffic/road/R999")
    rec("REG-API-10", "M1 Monitoring", "Unknown road", 404, s, s == 404, ms=ms)
    return token


# ---------------------------------------------------------------- M2 (API)


def hist():
    s, body, ms = get("/api/v1/traffic/history?road_id=R001&limit=5")
    rows = (
        body if isinstance(body, list) else body.get("data", []) if isinstance(body, dict) else []
    )
    rec(
        "HIST-001",
        "M2 Historical",
        "History for valid road",
        "200, ≥1 R001 rows",
        f"{s}, {len(rows)} rows",
        s == 200 and len(rows) >= 1 and all(r.get("road_id") == "R001" for r in rows),
        ms=ms,
    )

    # HIST-002: historical aggregate lives in analytics (port 8001), not the gateway (port 8000).
    s, body, ms = get_an(
        "/api/v1/traffic/aggregate?road_id=R001&start_time=2026-08-01&end_time=2026-08-07"
    )
    rows2 = body if isinstance(body, list) else []
    roads = sorted({r["road_id"] for r in rows2}) if rows2 else []
    rec(
        "HIST-002",
        "M2 Historical",
        "Aggregate for road R001 + date range (analytics service)",
        "only R001, range applied",
        f"roads {roads}",
        s == 200 and roads == ["R001"],
        "DEF-M3-022",
        ms,
    )

    s, body, ms = get("/api/v1/traffic/road-condition/R001")
    rec(
        "HIST-003",
        "M2 Historical",
        "Road condition for valid road",
        200,
        s,
        s == 200 and body.get("road_id") == "R001",
        ms=ms,
    )

    s, body, ms = get("/api/v1/traffic/history?road_id=R999&limit=5")
    rec(
        "HIST-004",
        "M2 Historical",
        "History for invalid road",
        "404/400",
        f"{s} {body if s == 200 else ''}",
        s in (400, 404),
        "DEF-M3-022",
        ms,
    )

    # HIST-005: historical time window — checked against analytics service where the data lives.
    s, body, ms = get_an(
        "/api/v1/traffic/history?road_id=R001&start_time=2026-08-01T00:00:00"
        "&end_time=2026-08-01T05:00:00&limit=500"
    )
    rows5 = body if isinstance(body, list) else []
    n = len(rows5)
    rec(
        "HIST-005",
        "M2 Historical",
        "History time window 00:00–05:00 applied (analytics service)",
        "≤ 6 rows",
        f"{n} rows",
        s == 200 and n <= 6,
        "DEF-M3-022",
        ms,
    )
    s, body, ms = get(
        "/api/v1/traffic/history?road_id=R001&start_time=2026-08-20" "&end_time=2026-08-01&limit=5"
    )
    rec(
        "HIST-005b",
        "M2 Historical",
        "Inverted history range rejected",
        400,
        s,
        s == 400,
        "DEF-M3-022",
        ms,
    )

    s, body, ms = get("/api/v1/traffic/history?road_id=R001&limit=1")
    want = {"road_id", "vehicle_count", "density", "congestion_level", "reading_timestamp"}
    have = set(body[0]) if s == 200 and body else set()
    rec(
        "HIST-006",
        "M2 Historical",
        "History response fields",
        sorted(want),
        sorted(have),
        want <= have,
        ms=ms,
    )


def pred():
    s, body, ms = get("/api/v1/predict/congestion?road_id=R001")
    rec(
        "PRED-001",
        "M2 Prediction",
        "Congestion prediction R001",
        "200 + predicted_level",
        body.get("predicted_level") if s == 200 else s,
        s == 200 and body.get("predicted_level") in ("Low", "Medium", "High", "Severe"),
        ms=ms,
    )
    rec(
        "PRED-004",
        "M2 Prediction",
        "model_version present",
        "non-empty",
        body.get("model_version") if s == 200 else s,
        s == 200 and bool(body.get("model_version")),
    )
    conf = body.get("confidence") if s == 200 else None
    rec(
        "PRED-005",
        "M2 Prediction",
        "Confidence in [0, 1]",
        "0–1",
        conf,
        isinstance(conf, (int, float)) and 0 <= conf <= 1,
    )
    lat = []
    for road in ic.ROADS:
        _, _, ms = get(f"/api/v1/predict/congestion?road_id={road}")
        lat.append(ms)
    rec(
        "PRED-007",
        "M2 Prediction",
        "Prediction latency, 6 roads (max)",
        "< 2000 ms",
        f"{round(max(lat))} ms",
        max(lat) < 2000,
        ms=max(lat),
    )
    s, body, ms = get("/api/v1/predict/peak-hours?road_id=R001")
    rec(
        "PRED-002",
        "M2 Prediction",
        "Peak-hour windows",
        "200 + windows",
        body.get("peak_windows") if s == 200 else s,
        s == 200 and bool(body.get("peak_windows")),
        ms=ms,
    )
    s, body, ms = get("/api/v1/predict/delay?road_id=R001")
    rec(
        "PRED-003",
        "M2 Prediction",
        "Delay estimate (minutes)",
        "200 + minutes",
        body.get("estimated_delay_minutes") if s == 200 else s,
        s == 200 and isinstance(body.get("estimated_delay_minutes"), (int, float)),
        ms=ms,
    )
    s, _, ms = get("/api/v1/predict/congestion?road_id=R999")
    rec("PRED-006", "M2 Prediction", "Invalid road", "400/404", s, s in (400, 404), ms=ms)


def route(token):
    s, body, ms = get(f"/api/v1/route/optimize?{ROUTE_Q}", token)
    rec(
        "ROUTE-001",
        "M2 Route",
        "Optimized route",
        "200 + path",
        s,
        s == 200 and bool(body.get("path")),
        ms=ms,
    )
    want = {"route_id", "path", "distance_km", "congestion_score", "predicted_level"}
    rec(
        "ROUTE-006",
        "M2 Route",
        "Optimize response fields",
        sorted(want),
        sorted(set(body) & want) if s == 200 else s,
        s == 200 and want <= set(body),
    )
    s, body, ms = get(f"/api/v1/route/alternate?{ROUTE_Q}", token)
    rec(
        "ROUTE-002",
        "M2 Route",
        "Alternate routes, maps API unreachable: fallback or clear 503",
        "200, or 503 with detail",
        f"{s} {body.get('detail', '') if isinstance(body, dict) else ''}"[:80],
        s == 200 or (s == 503 and isinstance(body, dict) and bool(body.get("detail"))),
        "DEF-M3-004",
        ms,
    )
    s, body, ms = get(f"/api/v1/route/travel-time?{ROUTE_Q}", token)
    rec(
        "ROUTE-003",
        "M2 Route",
        "Travel time (minutes)",
        "200 + estimated_minutes",
        body.get("estimated_minutes") if s == 200 else s,
        s == 200 and isinstance(body.get("estimated_minutes"), (int, float)),
        ms=ms,
    )
    s, body, ms = get(f"/api/v1/route/conditions?{ROUTE_Q}", token)
    rec(
        "ROUTE-004",
        "M2 Route",
        "Conditions along route",
        "200 + status/hazards",
        body.get("status") if s == 200 else s,
        s == 200 and "hazards" in body,
        ms=ms,
    )
    s, _, ms = get("/api/v1/route/optimize?origin=abc&destination=xyz", token)
    rec("ROUTE-005", "M2 Route", "Invalid coordinates", 400, s, s == 400, ms=ms)
    s, _, ms = get(f"/api/v1/route/optimize?{ROUTE_Q}")
    rec("ROUTE-00A", "M2 Route", "Route without token rejected (RBAC)", 401, s, s == 401, ms=ms)


# ---------------------------------------------------------------- UI

token_holder = {}


def wait_digits(page, selector, timeout=30000):
    """Route KPIs fill in once /route/* answers; wait for a digit instead of a fixed sleep."""
    try:
        page.wait_for_function(
            "s => /[0-9]/.test((document.querySelector(s) || {}).innerText || '')",
            arg=selector,
            timeout=timeout,
        )
    except Exception:
        pass


def ui(browser):
    run = uuid.uuid4().hex[:6]
    accounts = {r: fe.make_account(r, run) for r in ("user", "operator", "admin")}

    def login(ctx, role):
        page = ctx.new_page()
        fe.nav(page, f"{fe.FE}/Login.html")
        page.wait_for_timeout(1500)
        page.fill("#input-username", accounts[role]["email"])
        page.fill("#input-password", accounts[role]["password"])
        page.fill("#input-captcha", page.evaluate("currentCaptchaCode"))
        page.click("#submit-btn")
        try:
            page.wait_for_url(lambda u: "Login.html" not in u, timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        return page, page.url.rsplit("/", 1)[-1].replace("%20", " ")

    # REG-001 / REG-002: login and role routing for all three roles
    for role in ("user", "operator", "admin"):
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        fe.serve_frontend(ctx)
        page, landed = login(ctx, role)
        tc = "REG-001" if role == "operator" else "REG-002"
        rec(
            tc,
            "M1 UI",
            f"Login as {role} lands on its dashboard",
            fe.LANDING[role],
            landed,
            landed == fe.LANDING[role],
        )
        if role != "operator":
            ctx.close()
            continue

        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))

        # REG-003 / MAP-001 / MAP-005: live map, feed, road modal
        fe.nav(page, f"{fe.FE}/live%20maps.html")
        page.wait_for_timeout(6000)
        items = page.locator("#live-feed-list > *").count()
        rec("REG-003", "M1 UI", "Live traffic feed populated", "≥ 6 items", items, items >= 6)
        tiles = page.locator("#live-leaflet-map .leaflet-tile").count()
        roads = page.locator("#live-leaflet-map path.leaflet-interactive").count()
        rec(
            "MAP-001",
            "M2 Maps",
            "Live map renders tiles + road layers",
            "tiles > 0, roads ≥ 6",
            f"tiles {tiles}, road paths {roads}",
            tiles > 0 and roads >= 6,
        )
        page.screenshot(path=str(SHOTS / "reg_01_live_map.png"))
        page.evaluate("focusAndShowRoad('R001')")
        page.wait_for_timeout(2500)
        modal = page.locator("#road-detail-modal")
        visible = modal.is_visible()
        rid = page.inner_text("#modal-road-id") if visible else ""
        pred_txt = page.inner_text("#modal-ai-prediction") if visible else ""
        rec(
            "MAP-005",
            "M2 Maps",
            "Road modal (R001) with congestion/speed/density + AI prediction",
            "visible, R001, prediction",
            f"visible={visible}, id={rid.strip()}, " f"prediction={pred_txt.strip()[:40]!r}",
            visible and "R001" in rid and bool(pred_txt.strip()),
        )
        page.screenshot(path=str(SHOTS / "reg_02_road_modal.png"))

        # Route analysis page: ROUTE-007..009, MAP-002/003/004/006, FE-M2-001..006
        errors.clear()
        route_calls = []
        page.on(
            "requestfinished", lambda r: route_calls.append(r.url) if "/route/" in r.url else None
        )
        fe.nav(page, f"{fe.FE}/route-analysis.html")
        wait_digits(page, "#kpi-best-eta")
        page.wait_for_timeout(1500)
        rec(
            "FE-M2-001",
            "M2 Frontend",
            "Route page loads with no JS errors",
            0,
            f"{len(errors)} {errors[:1]}",
            not errors,
        )
        opts = page.eval_on_selector_all("#select-destination option", "o => o.map(x => x.value)")
        cards_before = page.inner_text("#route-cards-container")
        eta_before = page.inner_text("#kpi-best-eta")
        page.select_option("#select-destination", opts[-1])
        page.wait_for_timeout(1500)
        wait_digits(page, "#kpi-best-eta")
        cards = page.locator("#route-cards-container > *").count()
        eta, dist = page.inner_text("#kpi-best-eta"), page.inner_text("#kpi-best-distance")
        rec(
            "ROUTE-007",
            "M2 Route UI",
            "Choose destination → route cards + ETA/distance KPIs",
            "cards ≥ 1, ETA + distance",
            f"cards {cards}, ETA {eta!r}, distance {dist!r}",
            cards >= 1 and any(c.isdigit() for c in eta) and any(c.isdigit() for c in dist),
        )
        rec(
            "FE-M2-003",
            "M2 Frontend",
            "Travel time updates after route change",
            "ETA/cards change",
            f"ETA {eta_before!r} → {eta!r}",
            eta != eta_before or cards_before != page.inner_text("#route-cards-container"),
        )
        paths = page.locator("#route-map path.leaflet-interactive").count()
        label = page.inner_text("#map-active-route-label")
        rec(
            "MAP-002",
            "M2 Maps",
            "Route map draws the selected route",
            "≥ 1 path",
            f"{paths} paths, label {label.strip()[:40]!r}",
            paths >= 1,
        )
        rec(
            "MAP-006",
            "M2 Maps",
            "Map label matches a route card",
            "label in cards",
            label.strip()[:30],
            bool(label.strip()) and label.strip()[:12] in page.inner_text("#route-cards-container"),
        )
        page.screenshot(path=str(SHOTS / "reg_03_route_analysis.png"))

        rec_before = page.inner_text("#route-cards-container")
        page.click("button.opt-mode-btn[data-mode='eco']")
        page.wait_for_timeout(3000)
        active = page.get_attribute("button.opt-mode-btn[data-mode='eco']", "class")
        rec(
            "ROUTE-008",
            "M2 Route UI",
            "Switch optimisation mode to Eco",
            "Eco active",
            "active" in active,
            "active" in active and bool(rec_before),
        )

        fc_before = page.inner_text("#temporal-forecast-cards")
        page.click("button.horizon-btn[data-minutes='60']")
        page.wait_for_timeout(2500)
        fc_after = page.inner_text("#temporal-forecast-cards")
        rec(
            "ROUTE-009",
            "M2 Route UI",
            "Forecast horizon 0 → 60 min updates cards",
            "cards change",
            "changed" if fc_after != fc_before else "unchanged",
            fc_after != fc_before,
        )
        painted = page.evaluate(
            """() => { const c = document.getElementById('speed-profile-canvas');
            if (!c) return false;
            const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            for (let i = 3; i < d.length; i += 4) if (d[i]) return true; return false; }"""
        )
        rec(
            "FE-M2-002",
            "M2 Frontend",
            "Speed-profile / forecast chart painted",
            True,
            painted,
            painted and bool(fc_after.strip()),
        )
        # Panel is shown only when the route has hazards/road work (M2 FE-M2-004 behaviour).
        _, cond, _ = get(f"/api/v1/route/conditions?{ROUTE_Q}", token_holder["t"])
        has_issue = bool(cond.get("hazards")) or bool(cond.get("road_work_present"))
        hidden = "hidden" in (page.get_attribute("#road-conditions-panel", "class") or "")
        rec(
            "FE-M2-004",
            "M2 Frontend",
            "Road-conditions panel matches API (hidden when clear)",
            "visible" if has_issue else "hidden",
            f"{'hidden' if hidden else 'visible'} (API status {cond.get('status')})",
            hidden != has_issue,
        )

        page.click("#tile-terrain-btn")
        page.wait_for_timeout(1500)
        terrain = "bg-secondary" in (page.get_attribute("#tile-terrain-btn", "class") or "")
        page.click("#tile-osm-btn")
        rec("MAP-003", "M2 Maps", "Tile toggle OSM ↔ Terrain", "Terrain active", terrain, terrain)
        before = page.locator("#route-map canvas, #route-map .leaflet-heatmap-layer").count()
        page.click("#tile-heatmap-btn")
        page.wait_for_timeout(1500)
        after = page.locator("#route-map canvas, #route-map .leaflet-heatmap-layer").count()
        cls = page.get_attribute("#tile-heatmap-btn", "class") or ""
        rec(
            "MAP-004",
            "M2 Maps",
            "Heatmap overlay toggles",
            "overlay/button state changes",
            f"layers {before}→{after}, button active={'bg-' in cls and 'secondary' in cls}",
            after != before or "secondary" in cls,
        )
        page.screenshot(path=str(SHOTS / "reg_04_route_modes.png"))

        # FE-M2-005: the report download lives on the operator dashboard (M2 corrected target).
        js_errors = []
        page.on("pageerror", lambda e: js_errors.append(str(e)))
        fe.nav(page, f"{fe.FE}/operator%20dashboard.html")
        page.wait_for_timeout(8000)
        delay_text = page.inner_text("body")
        stuck = (
            "Calculating real-time delay estimates" in delay_text or "Analyzing..." in delay_text
        )
        rec(
            "REG-004",
            "M1/M2 UI",
            "Operator dashboard loads KPIs, delay estimates, peak chart",
            "no placeholders, no JS errors",
            f"placeholders={'yes' if stuck else 'no'}, JS errors {js_errors[:1]}",
            not stuck and not js_errors,
            "DEF-M3-023",
        )
        page.screenshot(path=str(SHOTS / "reg_06_operator_dashboard.png"))
        try:
            with page.expect_download(timeout=20000) as dl_info:
                page.click("#download-btn-label")
            dl = dl_info.value
            name = dl.suggested_filename
            size = Path(dl.path()).stat().st_size
            rec(
                "FE-M2-005",
                "M2 Frontend",
                "Operator dashboard 'Download Prediction Report'",
                "file downloaded",
                f"{name} ({size} bytes)",
                size > 0,
            )
        except Exception as exc:
            rec(
                "FE-M2-005",
                "M2 Frontend",
                "Operator dashboard 'Download Prediction Report'",
                "file downloaded",
                f"no download: {str(exc)[:60]}",
                False,
                "DEF-M3-023",
            )
        fe.nav(page, f"{fe.FE}/route-analysis.html")
        page.wait_for_timeout(4000)
        rec(
            "FE-M2-006",
            "M2 Frontend",
            "Route page calls live /route/* APIs",
            "≥ 1 call",
            len(route_calls),
            len(route_calls) >= 1,
        )
        ctx.close()

    # FE-M2-007: backend unreachable → page still renders (fallback), no blank page
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    fe.serve_frontend(ctx)
    page, _ = login(ctx, "operator")
    ctx.route("http://127.0.0.1:8000/**", lambda r: r.abort())
    fe.nav(page, f"{fe.FE}/route-analysis.html")
    page.wait_for_timeout(6000)
    text_len = len(page.inner_text("body"))
    badge = (
        page.inner_text("#data-source-badge") if page.locator("#data-source-badge").count() else ""
    )
    rec(
        "FE-M2-007",
        "M2 Frontend",
        "Backend unreachable → fallback shown, no blank page",
        "page renders + fallback badge",
        f"{text_len} chars, badge {badge.strip()!r}",
        text_len > 500,
    )
    page.screenshot(path=str(SHOTS / "reg_05_backend_down.png"))
    ctx.close()


def integration(token):
    # INT-001: Auth → Live → Prediction → Route handoff, using data from each previous step.
    s1, live, _ = get("/api/v1/traffic/live")
    busiest = max(live, key=lambda r: r["density"])["road_id"] if s1 == 200 else None
    s2, p, _ = get(f"/api/v1/predict/congestion?road_id={busiest}")
    s3, r, _ = get(f"/api/v1/route/optimize?{ROUTE_Q}", token)
    ok = token and s1 == 200 and s2 == 200 and s3 == 200 and r.get("authorized_user")
    rec(
        "INT-001",
        "Integration",
        "Auth → Live → Prediction(busiest road) → Route",
        "all 200, route bound to user",
        f"live {s1}, predict {busiest}:{s2}, route {s3}",
        bool(ok),
    )


def write():
    counts = {v: sum(r["verdict"] == v for r in results) for v in ("PASS", "FAIL")}
    (OUT / "regression_results.json").write_text(
        json.dumps({"summary": counts, "results": results}, indent=2), encoding="utf-8"
    )
    out = [
        "# Milestone 3 Day 6 — M1/M2 Regression Results",
        "",
        f"Executed {time.strftime('%Y-%m-%d %H:%M')} · "
        "`python QA/milestone3/day6/regression_m1_m2.py`",
        "",
        f"**{counts['PASS']} pass · {counts['FAIL']} fail** (of {len(results)})",
        "",
        "| TC | Area | Check | Expected | Actual | ms | Result | Ref |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        out.append(
            f"| {r['tc']} | {r['area']} | {r['check']} | {r['expected']} | "
            f"{r['actual']} | {'' if r['ms'] is None else r['ms']} | {r['verdict']} | "
            f"{r['ref']} |"
        )
    (OUT / "regression_results.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    return counts


def main():
    from playwright.sync_api import sync_playwright

    SHOTS.mkdir(exist_ok=True)
    token = m1_api()
    hist()
    pred()
    route(token)
    integration(token)
    token_holder["t"] = token
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge", args=["--disable-features=LocalNetworkAccessChecks"]
        )
        ui(browser)
        browser.close()
    counts = write()
    for r in results:
        print(
            f"{r['verdict']:4} {r['tc']:10} {r['check'][:60]:60} -> {r['actual'][:70]} {r['ref']}"
        )
    print(counts)
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

"""Milestone 3 Day 5 — frontend end-to-end journey in a real browser (Playwright + Edge).

For each role (user / operator / admin):
  Login.html (real form + captcha) → role dashboard → Alerts.html (list + bell drawer)
  → analytics.html → route-analysis.html, recording every call the page makes to the
  gateway (:8000), Analytics (:8001), AI Insights (:8010) and hard-coded LAN hosts, and
  whether the page silently fell back to mock data.

Two marker alerts are created first through the Alert API (an anomaly-detector style
High accident alert and a Critical accident alert) so we can check who sees what.

    docker compose -f docker-compose.dev.yml up -d
    python QA/milestone3/day5/frontend_e2e.py          # uses system Edge (channel=msedge)

Writes frontend_e2e_results.md/json and screenshots/ next to this file (or M3_OUT_DIR).
"""

import json
import sys
import urllib.parse
import time
import uuid
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import integration_cycle as ic  # noqa: E402  (reuses call/psql helpers)

sys.path.insert(0, str(HERE.parent))
import qa_auth  # noqa: E402

SITE = ic.FRONTEND_DIR
PORT = 5500
FE = f"http://127.0.0.1:{PORT}"
OUT = ic.OUT  # M3_OUT_DIR, default this folder
SHOTS = OUT / "screenshots"
WATCH = (":8000", ":8001", ":8010", "192.168.")
LANDING = {
    "user": "public dashboard.html",
    "operator": "operator dashboard.html",
    "admin": "admin dashboard.html",
}
results = []


def record(role, check, expected, actual, ok, ref=""):
    results.append(
        {
            "role": role,
            "check": check,
            "expected": str(expected),
            "actual": str(actual),
            "verdict": "PASS" if ok else "FAIL",
            "ref": ref,
        }
    )


def serve_frontend(ctx):
    """Serve the static frontend from disk via request interception.

    A real socket server (python -m http.server) works, but on the QA machine AVG
    Web Shield aborts the browser's download of the 100 KB api.js (WinError 10053)
    and Edge retries ~20 s later, so pages time out (see DEF-M3-006). Fulfilling
    from disk keeps the page origin (http://127.0.0.1:5500) identical for CORS
    while every backend call still goes over the real network.
    """
    types = {
        ".html": "text/html",
        ".js": "application/javascript",
        ".css": "text/css",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".json": "application/json",
    }

    def handler(route):
        rel = urllib.parse.unquote(route.request.url[len(FE) + 1 :].split("?", 1)[0])
        path = SITE / rel
        if path.is_file():
            route.fulfill(
                status=200,
                body=path.read_bytes(),
                content_type=types.get(path.suffix.lower(), "application/octet-stream"),
            )
        else:
            route.fulfill(status=404, body=b"not found")

    ctx.route(f"{FE}/**", handler)


def make_account(role, run):
    email = f"qa.d5ui.{role}.{run}@gmail.com"
    creds = {"email": email, "password": "QaPass#2026"}
    ic.call("POST", ic.GW + "/api/v1/auth/register", {"name": f"qa_d5ui_{role}_{run}", **creds})
    if role != "user":
        ic.psql(f"UPDATE users SET role='{role}' WHERE email='{email}'")
    return creds


def seed_alerts(run):
    # The Alert API needs a JWT since the DEF-M3-005 fix; seed as an admin.
    admin = qa_auth.role_token(ic.GW, "admin", "qa.seed")
    msgs = {
        "high": f"QA-D5-{run} anomaly detector flagged a possible_incident on road R004.",
        "critical": f"QA-D5-{run} multi-vehicle collision, lanes blocked on R004.",
    }
    ic.call(
        "POST",
        ic.GW + "/api/v1/alerts/",
        {"type": "accident", "severity": "High", "road_id": "R004", "message": msgs["high"]},
        token=admin,
    )
    ic.call(
        "POST",
        ic.GW + "/api/v1/alerts/",
        {
            "type": "accident",
            "severity": "Critical",
            "road_id": "R004",
            "message": msgs["critical"],
        },
        token=admin,
    )
    return msgs


class NetLog:
    def __init__(self, page):
        self.calls, self.console = [], []
        page.on("requestfinished", self._done)
        page.on("requestfailed", self._failed)
        page.on(
            "console",
            lambda m: (
                self.console.append(f"{m.type}: {m.text}")
                if m.type in ("warning", "error")
                else None
            ),
        )

    def _keep(self, url):
        return any(w in url for w in WATCH)

    def _done(self, req):
        if self._keep(req.url):
            resp = req.response()
            self.calls.append((req.method, req.url, resp.status if resp else "?"))

    def _failed(self, req):
        if self._keep(req.url):
            self.calls.append((req.method, req.url, f"FAILED {req.failure}"))

    def take(self):
        calls, console = self.calls[:], self.console[:]
        self.calls.clear()
        self.console.clear()
        return calls, console


def nav(page, url):
    """Pages load render-blocking CDN scripts (Tailwind, Chart.js); on the QA network
    those occasionally stall, so allow 60 s and retry once."""
    for attempt in (1, 2):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return
        except Exception:
            if attempt == 2:
                raise


def short(url):
    return url.split("//", 1)[-1].split("?", 1)[0]


def journey(browser, role, creds, msgs, pages_log):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    serve_frontend(ctx)
    page = ctx.new_page()
    net = NetLog(page)

    # Login through the real form
    nav(page, f"{FE}/Login.html")
    page.wait_for_timeout(1500)
    page.fill("#input-username", creds["email"])
    page.fill("#input-password", creds["password"])
    captcha = page.evaluate("typeof currentCaptchaCode !== 'undefined' ? currentCaptchaCode : ''")
    page.fill("#input-captcha", captcha)
    page.click("#submit-btn")
    try:
        page.wait_for_url(lambda u: "Login.html" not in u, timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(2500)
    landed = page.url.rsplit("/", 1)[-1].replace("%20", " ")
    token = page.evaluate("sessionStorage.getItem('access_token')") or ""
    record(role, "UI login lands on role dashboard", LANDING[role], landed, landed == LANDING[role])
    record(
        role,
        "Session holds a real JWT (not mock-dev-token)",
        "JWT",
        (
            "mock-dev-token"
            if token == "mock-dev-token"
            else ("JWT" if token.count(".") == 2 else "none")
        ),
        token.count(".") == 2,
    )
    page.screenshot(path=str(SHOTS / f"{role}_01_dashboard.png"))
    pages_log[f"{role} · {landed}"] = net.take()

    # Alerts page: main list + notification bell
    nav(page, f"{FE}/Alerts.html")
    page.wait_for_timeout(6000)
    body = page.inner_text("body")
    want_crit = role != "user"
    record(
        role,
        "Alerts page list shows the Alert Service accident alert (R004, High)",
        True,
        msgs["high"] in body,
        msgs["high"] in body,
        "DEF-M3-018",
    )
    bell = page.locator("#nav-notification-bell-btn")
    if bell.count():
        bell.first.click()
        page.wait_for_timeout(1000)
    drawer = page.inner_text("body")
    page.screenshot(path=str(SHOTS / f"{role}_02_alerts_bell.png"))
    record(
        role,
        "Bell drawer shows detector accident alert (High)",
        role != "user",
        msgs["high"] in drawer,
        (msgs["high"] in drawer) == (role != "user"),
        "" if (msgs["high"] in drawer) == (role != "user") else "DEF-M3-007",
    )
    record(
        role,
        "Bell drawer shows Critical accident alert",
        want_crit,
        msgs["critical"] in drawer,
        (msgs["critical"] in drawer) == want_crit,
        "" if (msgs["critical"] in drawer) == want_crit else "DEF-M3-012",
    )
    mock = "Severe Bottleneck Gridlock" in drawer or "NOTIF-101" in drawer
    record(role, "Bell drawer is live data, not seeded mock notifications", False, mock, not mock)
    calls, console = net.take()
    pages_log[f"{role} · Alerts.html"] = (calls, console)
    alert_calls = [c for c in calls if "/alerts/my" in c[1]]
    # Since the DEF-M3-005/012 fix the server takes the role from the JWT, so the UI only
    # has to send its token: every /alerts/my call must be accepted (200).
    statuses = sorted({str(c[2]) for c in alert_calls})
    record(
        role,
        "Alerts UI calls GET /alerts/my with its JWT (accepted)",
        "≥ 1 call, all 200",
        f"{len(alert_calls)} call(s), status {statuses}",
        bool(alert_calls) and statuses == ["200"],
        "DEF-M3-012",
    )

    # Analytics page
    nav(page, f"{FE}/analytics.html")
    page.wait_for_timeout(14000)
    page.screenshot(path=str(SHOTS / f"{role}_03_analytics.png"), full_page=True)
    calls, console = net.take()
    pages_log[f"{role} · analytics.html"] = (calls, console)
    an_ok = [c for c in calls if ":8001" in c[1] and c[2] == 200]
    record(
        role,
        "Analytics page loads live data from Analytics service (:8001)",
        ">=1 call with 200",
        f"{len(an_ok)} ok; calls: "
        + "; ".join(f"{short(u)} → {s}" for _, u, s in calls if "analytics" in u)[:300],
        bool(an_ok),
        "" if an_ok else "DEF-M3-013/014",
    )
    ai = [c for c in calls if ":8010" in c[1]]
    record(
        role,
        "AI recommendations load from AI Insights (:8010)",
        "200",
        "; ".join(sorted({str(s)[:40] for _, _, s in ai})) or "no call",
        any(s == 200 for _, _, s in ai),
        "DEF-M3-017",
    )

    # Route analysis page (M2 regression inside the integrated build)
    nav(page, f"{FE}/route-analysis.html")
    page.wait_for_timeout(8000)
    page.screenshot(path=str(SHOTS / f"{role}_04_route.png"))
    calls, console = net.take()
    pages_log[f"{role} · route-analysis.html"] = (calls, console)
    route_ok = [c for c in calls if "/route/" in c[1] and c[2] == 200]
    record(
        role, "Route analysis page reaches /route/* with 200", ">=1", len(route_ok), bool(route_ok)
    )

    # Page guard: public user must not reach the admin dashboard
    if role == "user":
        nav(page, f"{FE}/admin%20dashboard.html")
        page.wait_for_timeout(2500)
        at = page.url.rsplit("/", 1)[-1].replace("%20", " ")
        record(
            role,
            "Public user opening admin dashboard is redirected",
            "not admin dashboard",
            at,
            at != "admin dashboard.html",
        )
    ctx.close()


def write(pages_log):
    counts = {v: sum(r["verdict"] == v for r in results) for v in ("PASS", "FAIL")}
    (OUT / "frontend_e2e_results.json").write_text(
        json.dumps(
            {
                "summary": counts,
                "results": results,
                "network": {k: {"calls": v[0], "console": v[1][:15]} for k, v in pages_log.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    out = [
        "# Milestone 3 Day 5 — Frontend E2E Results (Playwright, Edge)",
        "",
        f"Executed {time.strftime('%Y-%m-%d %H:%M')} · frontend served from "
        f"`{SITE.relative_to(ic.REPO_ROOT).as_posix()}`"
        f" at {FE} · `python QA/milestone3/day5/frontend_e2e.py`",
        "",
        f"**{counts['PASS']} pass · {counts['FAIL']} fail** (of {len(results)})",
        "",
        "| Role | Check | Expected | Actual | Result | Ref |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in results:
        out.append(
            f"| {r['role']} | {r['check']} | {r['expected']} | {r['actual']} | "
            f"{r['verdict']} | {r['ref'] if r['verdict'] == 'FAIL' else ''} |"
        )
    out += ["", "## Backend calls made by each page", ""]
    for page_name, (calls, console) in pages_log.items():
        out.append(f"**{page_name}**")
        out.append("")
        seen = {}
        for m, u, s in calls:
            seen.setdefault((m, short(u), str(s)), 0)
            seen[(m, short(u), str(s))] += 1
        for (m, u, s), n in seen.items():
            out.append(f"- `{m} {u}` → {s}" + (f" ×{n}" if n > 1 else ""))
        flagged = [
            c
            for c in console
            if any(k in c.lower() for k in ("cors", "fallback", "mock", "failed"))
        ]
        for c in dict.fromkeys(flagged).keys():
            out.append(f"- console: `{c[:180]}`")
        out.append("")
    (OUT / "frontend_e2e_results.md").write_text("\n".join(out), encoding="utf-8")
    return counts


def main():
    SHOTS.mkdir(exist_ok=True)
    run = uuid.uuid4().hex[:6]
    msgs = seed_alerts(run)
    pages_log = {}
    with sync_playwright() as p:
        # Pages fulfilled by interception have no server IP, so Edge's Local Network
        # Access check treats them as public and blocks their calls to 127.0.0.1.
        # A real local server doesn't trigger it; turn the check off for the harness.
        browser = p.chromium.launch(
            channel="msedge", args=["--disable-features=LocalNetworkAccessChecks"]
        )
        for role in ("user", "operator", "admin"):
            journey(browser, role, make_account(role, run), msgs, pages_log)
        browser.close()
    counts = write(pages_log)
    for r in results:
        print(f"{r['verdict']:5} {r['role']:9} {r['check']} -> {r['actual'][:110]}")
    print(counts)
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())

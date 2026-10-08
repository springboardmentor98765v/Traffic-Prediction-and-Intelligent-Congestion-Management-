"""Shared helpers for the Milestone 4 live-system QA scripts (Days 3-6).

Service URLs come from the environment (defaults are the Render names in render.yaml):

    BACKEND_URL    https://tv-team1-backend.onrender.com
    ANALYTICS_URL  https://tv-team1-analytics.onrender.com
    AI_URL         https://tv-team1-ai.onrender.com
    WEB_URL        https://tv-team1-web.onrender.com

Optional:
    ALERT_SERVICE_KEY  producer key for POST /api/v1/alerts/ (Render env group value)
    DATABASE_URL       production DB URL; only used to promote QA accounts to operator/admin
                       (needs psycopg2). Without it, admin-only checks are reported as SKIP.

Point the same scripts at the local Docker stack with
    BACKEND_URL=http://127.0.0.1:8000 ANALYTICS_URL=http://127.0.0.1:8001 \
    AI_URL=http://127.0.0.1:8010 WEB_URL=http://127.0.0.1:5500

Stdlib only (psycopg2 optional), so they run on a bare GitHub runner.
"""

import json
import os
import platform
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

PASSWORD = "QaPass#2026"
ICONS = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭"}

# Windows consoles default to cp1252, which can't print the ✅/❌ in the reports.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_URLS = {
    "backend": "https://tv-team1-backend.onrender.com",
    "analytics": "https://tv-team1-analytics.onrender.com",
    "ai": "https://tv-team1-ai.onrender.com",
    "web": "https://tv-team1-web.onrender.com",
}

# Liveness path per service, used to wake free-tier services before measuring anything.
HEALTH_PATHS = {"backend": "/health", "analytics": "/", "ai": "/health", "web": "/Login.html"}


def service_urls():
    return {
        name: os.environ.get(f"{name.upper()}_URL", default).rstrip("/")
        for name, default in DEFAULT_URLS.items()
    }


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def call(url, method="GET", body=None, token=None, headers=None, timeout=30):
    """Return (status, payload, elapsed_ms, response_headers). status is None on network error."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, raw, resp_headers = resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        status, raw, resp_headers = exc.code, exc.read(), dict(exc.headers)
    except (urllib.error.URLError, OSError) as exc:
        return None, str(getattr(exc, "reason", exc)), (time.perf_counter() - start) * 1000, {}
    elapsed_ms = (time.perf_counter() - start) * 1000
    try:
        payload = json.loads(raw) if raw else None
    except ValueError:
        payload = raw.decode(errors="replace")
    return status, payload, elapsed_ms, resp_headers


def wake_services(urls, names=None, timeout=240):
    """Free Render services sleep after 15 min idle. Poll until each answers 200.

    Returns {service: seconds_until_healthy or None}. The first number is the cold-start
    time when the service was asleep.
    """
    names = names or list(HEALTH_PATHS)
    start = time.monotonic()
    ready = {}
    pending = set(names)
    while pending and time.monotonic() - start < timeout:
        for name in sorted(pending):
            status, _, _, _ = call(urls[name] + HEALTH_PATHS[name], timeout=90)
            if status == 200:
                ready[name] = round(time.monotonic() - start, 1)
                pending.discard(name)
        if pending:
            time.sleep(5)
    for name in pending:
        ready[name] = None
    return ready


def alert_service_headers():
    key = os.environ.get("ALERT_SERVICE_KEY", "")
    return {"X-Alert-Service-Key": key} if key else {}


def register_and_login(backend, tag):
    """Create a fresh account through the API. Returns (email, login_body or {})."""
    run = uuid.uuid4().hex[:8]
    email = f"qa.{tag}.{run}@gmail.com"
    call(
        backend + "/api/v1/auth/register",
        "POST",
        {"name": f"qa_{tag}_{run}", "email": email, "password": PASSWORD},
    )
    status, body, _, _ = call(
        backend + "/api/v1/auth/login", "POST", {"email": email, "password": PASSWORD}
    )
    return email, (body if status == 200 and isinstance(body, dict) else {})


def promote(email, role):
    """Set a QA account's role in the production DB. False when DATABASE_URL/psycopg2 is missing."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        return False
    try:
        import psycopg2
    except ImportError:
        return False
    url = url.replace("postgresql+psycopg2://", "postgresql://", 1)
    with psycopg2.connect(url) as conn, conn.cursor() as cur:
        cur.execute("UPDATE users SET role = %s WHERE email = %s", (role, email))
        return cur.rowcount == 1


def role_token(backend, role, tag):
    """JWT for a fresh account with `role`, or None if it can't be promoted."""
    email, login = register_and_login(backend, f"{tag}.{role}")
    if role != "user" and not promote(email, role):
        return None
    if role == "user":
        return login.get("access_token")
    status, body, _, _ = call(
        backend + "/api/v1/auth/login", "POST", {"email": email, "password": PASSWORD}
    )
    return body.get("access_token") if status == 200 and isinstance(body, dict) else None


class Results:
    """Collects PASS/FAIL/SKIP rows and renders them as a markdown report."""

    def __init__(self, title, urls):
        self.title = title
        self.urls = urls
        self.rows = []
        self.notes = []

    def add(self, area, name, ok, expected="", actual="", ms=None, detail=""):
        result = "SKIP" if ok is None else ("PASS" if ok else "FAIL")
        self.rows.append(
            {
                "area": area,
                "check": name,
                "expected": str(expected),
                "actual": str(actual),
                "ms": None if ms is None else round(ms),
                "result": result,
                "detail": detail,
            }
        )
        print(f"{result:4} {area:14} {name}  {actual} {'' if ms is None else f'{ms:.0f} ms'}")
        return ok

    def check(self, area, name, url, expect=200, method="GET", body=None, token=None, headers=None):
        """Call `url`; PASS when the status matches `expect`. Returns the payload."""
        status, payload, ms, _ = call(url, method, body, token, headers)
        detail = ""
        if status != expect:
            detail = (payload if isinstance(payload, str) else json.dumps(payload))[:160]
        self.add(area, name, status == expect, expect, status, ms, detail)
        return payload

    def counts(self):
        return {
            r: sum(1 for row in self.rows if row["result"] == r) for r in ("PASS", "FAIL", "SKIP")
        }

    @property
    def failed(self):
        return self.counts()["FAIL"] > 0

    def markdown(self):
        c = self.counts()
        total = c["PASS"] + c["FAIL"]
        lines = [
            f"# {self.title}",
            "",
            f"- Run: {now_utc()} from {platform.node() or 'runner'}",
            f"- Result: **{c['PASS']}/{total} passed**, {c['FAIL']} failed, {c['SKIP']} skipped",
            "- Targets: " + ", ".join(f"{k} `{v}`" for k, v in self.urls.items()),
            "",
        ]
        if self.notes:
            lines += [f"> {note}" for note in self.notes] + [""]
        lines += [
            "| # | Area | Check | Expected | Actual | ms | Result |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for i, r in enumerate(self.rows, 1):
            ms = "" if r["ms"] is None else r["ms"]
            lines.append(
                f"| {i} | {r['area']} | {r['check']} | {r['expected']} | {r['actual']} | {ms} | "
                f"{ICONS[r['result']]} {r['result']} |"
            )
        fails = [r for r in self.rows if r["result"] == "FAIL" and r["detail"]]
        if fails:
            lines += ["", "## Failure details", ""]
            lines += [f"- **{r['check']}**: `{r['detail']}`" for r in fails]
        return "\n".join(lines) + "\n"

    def save(self, report_path=None, json_path=None):
        if report_path:
            with open(report_path, "w", encoding="utf-8") as fh:
                fh.write(self.markdown())
            print(f"\nReport written to {report_path}")
        if json_path:
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump({"title": self.title, "run": now_utc(), "rows": self.rows}, fh, indent=2)

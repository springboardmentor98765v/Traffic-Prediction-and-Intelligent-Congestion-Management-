"""Milestone 4 Day 5 — performance and responsiveness checks on the live platform (FR-07).

Measures, against the deployed services:

1. Cold start: time for a sleeping free-tier service to answer (run after >15 min idle
   to capture it; otherwise it shows the warm number).
2. Warm API latency: N sequential requests per key endpoint -> p50 / p95 / max / errors.
3. Concurrency: U parallel users hitting the busiest read endpoints -> p95 and throughput.
4. Page delivery: time and size of every frontend page plus api.js.

Every endpoint or page over its threshold becomes a row in the defect list at the end of
the report (priority by how far over it is), ready to copy into the defect tracker.

    python QA/milestone4/day5/performance_check.py --report QA/milestone4/day5/performance_report.md

Thresholds (agreed for the free tier: 0.1 CPU / 512 MB per service, Singapore region):
    API p95 (warm, sequential)  <= 1000 ms     heavy AI/ML endpoints <= 2500 ms
    API p95 under 10 users      <= 3000 ms
    Page delivery               <= 2000 ms
    Error rate                  0 %
Override with --api-p95 / --heavy-p95 / --load-p95 / --page-ms.
"""

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from live_common import call, now_utc, register_and_login, service_urls, wake_services  # noqa: E402

ROAD = "R001"
ROUTE_Q = "origin=11.9416,79.8083&destination=11.9350,79.8100"

# (service, label, path, needs_token, heavy)
ENDPOINTS = [
    ("backend", "Health", "/health", False, False),
    ("backend", "Live traffic", "/api/v1/traffic/live", False, False),
    ("backend", "Road detail", f"/api/v1/traffic/road/{ROAD}", False, False),
    ("backend", "Density", "/api/v1/traffic/density", False, False),
    (
        "backend",
        "Hourly metrics",
        f"/api/v1/traffic/metrics/hourly?road_id={ROAD}&limit=24",
        False,
        False,
    ),
    ("backend", "Auth /me", "/api/v1/auth/me", True, False),
    ("backend", "My alerts", "/api/v1/alerts/my", True, False),
    ("backend", "Predict congestion", f"/api/v1/predict/congestion?road_id={ROAD}", False, True),
    ("backend", "Route optimize", f"/api/v1/route/optimize?{ROUTE_Q}", True, True),
    ("analytics", "Analytics live", "/api/v1/traffic/live", False, False),
    ("analytics", "Trends", f"/analytics/trends?road_id={ROAD}", False, False),
    ("analytics", "Heatmap", "/analytics/heatmap", False, False),
    ("analytics", "Report CSV", f"/analytics/reports?road_id={ROAD}&limit=500", False, False),
    ("ai", "AI health", "/health", False, False),
    ("ai", "Anomalies", f"/api/v1/ai/anomalies?road_id={ROAD}", False, True),
    ("ai", "Recommendations", f"/api/v1/ai/recommendations?road_id={ROAD}", False, True),
]

LOAD_ENDPOINTS = [
    ("backend", "Live traffic", "/api/v1/traffic/live"),
    ("analytics", "Trends", f"/analytics/trends?road_id={ROAD}"),
    ("ai", "Recommendations", f"/api/v1/ai/recommendations?road_id={ROAD}"),
]

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


def pct(values, p):
    if not values:
        return None
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, round(p / 100 * len(ordered) + 0.5) - 1))
    return ordered[k]


def measure(url, n, token=None):
    times, errors = [], 0
    call(url, token=token, timeout=90)  # warm-up, not counted
    for _ in range(n):
        status, _, ms, _ = call(url, token=token, timeout=60)
        if status == 200:
            times.append(ms)
        else:
            errors += 1
    return times, errors


def load_test(url, users, per_user):
    def worker(_):
        out = []
        for _ in range(per_user):
            status, _, ms, _ = call(url, timeout=60)
            out.append((status, ms))
        return out

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as pool:
        results = [row for chunk in pool.map(worker, range(users)) for row in chunk]
    wall = time.perf_counter() - start
    ok = [ms for status, ms in results if status == 200]
    return ok, len(results) - len(ok), len(results) / wall if wall else 0.0


def mark(ok):
    return "✅" if ok else "❌"


def fmt(ms):
    return "-" if ms is None else f"{ms:.0f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    parser.add_argument("--json")
    parser.add_argument("-n", type=int, default=20, help="sequential requests per endpoint")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--per-user", type=int, default=5)
    parser.add_argument("--api-p95", type=float, default=1000)
    parser.add_argument("--heavy-p95", type=float, default=2500)
    parser.add_argument("--load-p95", type=float, default=3000)
    parser.add_argument("--page-ms", type=float, default=2000)
    args = parser.parse_args()

    urls = service_urls()
    findings = []  # (area, item, measured, threshold)
    data = {"run": now_utc(), "urls": urls}

    print("1. Cold start / wake-up")
    cold = wake_services(urls)
    data["cold_start_s"] = cold
    for name, seconds in cold.items():
        print(f"   {name:10} {seconds} s")
        if seconds is None:
            findings.append(
                ("Availability", f"{name} did not come up", "no 200 in 240 s", "reachable")
            )

    _, login = register_and_login(urls["backend"], "m4d5")
    token = login.get("access_token")

    print(f"2. Warm latency ({args.n} sequential requests each)")
    latency = []
    for service, label, path, needs_token, heavy in ENDPOINTS:
        times, errors = measure(urls[service] + path, args.n, token if needs_token else None)
        limit = args.heavy_p95 if heavy else args.api_p95
        row = {
            "service": service,
            "endpoint": label,
            "path": path,
            "p50": statistics.median(times) if times else None,
            "p95": pct(times, 95),
            "max": max(times) if times else None,
            "errors": errors,
            "limit": limit,
        }
        row["ok"] = errors == 0 and row["p95"] is not None and row["p95"] <= limit
        latency.append(row)
        print(
            f"   {service:9} {label:20} p50 {fmt(row['p50']):>5}  "
            f"p95 {fmt(row['p95']):>5}  err {errors}"
        )
        if errors:
            findings.append(
                ("API errors", f"{service} {label}", f"{errors}/{args.n} failed", "0 errors")
            )
        if row["p95"] is not None and row["p95"] > limit:
            findings.append(
                (
                    "API latency",
                    f"{service} {label}",
                    f"p95 {row['p95']:.0f} ms",
                    f"<= {limit:.0f} ms",
                )
            )
    data["latency"] = latency

    print(f"3. Concurrency ({args.users} users x {args.per_user} requests)")
    load = []
    for service, label, path in LOAD_ENDPOINTS:
        ok, errors, rps = load_test(urls[service] + path, args.users, args.per_user)
        row = {
            "service": service,
            "endpoint": label,
            "p50": statistics.median(ok) if ok else None,
            "p95": pct(ok, 95),
            "errors": errors,
            "rps": rps,
        }
        row["ok"] = errors == 0 and row["p95"] is not None and row["p95"] <= args.load_p95
        load.append(row)
        print(f"   {service:9} {label:16} p95 {fmt(row['p95']):>5}  {rps:.1f} req/s  err {errors}")
        if errors:
            findings.append(("Load errors", f"{service} {label}", f"{errors} failed", "0 errors"))
        if row["p95"] is not None and row["p95"] > args.load_p95:
            findings.append(
                (
                    "Load latency",
                    f"{service} {label}",
                    f"p95 {row['p95']:.0f} ms",
                    f"<= {args.load_p95:.0f} ms",
                )
            )
    data["load"] = load

    print("4. Page delivery")
    pages = []
    for page in PAGES:
        status, body, ms, _ = call(f"{urls['web']}/{page.replace(' ', '%20')}", timeout=60)
        size = len(body.encode()) if isinstance(body, str) else 0
        row = {"page": page, "status": status, "ms": ms, "kb": size / 1024}
        row["ok"] = status == 200 and ms <= args.page_ms
        pages.append(row)
        print(f"   {page:26} {status} {ms:6.0f} ms {row['kb']:7.1f} KB")
        if not row["ok"]:
            findings.append(
                ("Page load", page, f"{status}, {ms:.0f} ms", f"200, <= {args.page_ms:.0f} ms")
            )
    data["pages"] = pages
    data["findings"] = findings

    # ------------------------------------------------------------------ report
    lines = [
        "# Milestone 4 Day 5 — Performance Report (live environment)",
        "",
        f"- Run: {data['run']}",
        "- Targets: " + ", ".join(f"{k} `{v}`" for k, v in urls.items()),
        f"- Thresholds: API p95 <= {args.api_p95:.0f} ms (heavy AI/ML <= {args.heavy_p95:.0f} ms), "
        f"p95 under {args.users} users <= {args.load_p95:.0f} ms, "
        f"page <= {args.page_ms:.0f} ms, 0 errors",
        f"- Verdict: **{'PASS' if not findings else f'{len(findings)} finding(s)'}**",
        "",
        "## 1. Cold start (free tier sleeps after 15 min idle)",
        "",
        "| Service | Time to first 200 (s) |",
        "| --- | --- |",
    ]
    lines += [f"| {k} | {v if v is not None else 'not reachable'} |" for k, v in cold.items()]
    lines += [
        "",
        "Only a real cold start if the run began after at least 15 minutes of no traffic.",
        "",
        f"## 2. Warm API latency ({args.n} sequential requests, ms)",
        "",
        "| Service | Endpoint | p50 | p95 | max | Errors | Limit | Result |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in latency:
        lines.append(
            f"| {row['service']} | {row['endpoint']} | {fmt(row['p50'])} | {fmt(row['p95'])} | "
            f"{fmt(row['max'])} | {row['errors']} | {row['limit']:.0f} | {mark(row['ok'])} |"
        )
    lines += [
        "",
        f"## 3. Concurrency ({args.users} users x {args.per_user} requests)",
        "",
        "| Service | Endpoint | p50 | p95 | req/s | Errors | Result |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in load:
        lines.append(
            f"| {row['service']} | {row['endpoint']} | {fmt(row['p50'])} | {fmt(row['p95'])} | "
            f"{row['rps']:.1f} | {row['errors']} | {mark(row['ok'])} |"
        )
    lines += [
        "",
        "## 4. Page delivery (HTML/JS download from the static host)",
        "",
        "| Page | Status | ms | Size (KB) | Result |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in pages:
        lines.append(
            f"| {row['page']} | {row['status']} | {row['ms']:.0f} | {row['kb']:.1f} "
            f"| {mark(row['ok'])} |"
        )
    lines += [
        "",
        "Browser rendering (Tailwind CDN, Chart.js, Leaflet) is not included; measure it with",
        "Chrome DevTools -> Lighthouse on each page (Intern 4's cross-browser pass).",
        "",
        "## 5. Defect list (prioritised)",
        "",
    ]
    if findings:
        lines += [
            "| # | Priority | Area | Item | Measured | Expected |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for i, (area, item, measured, expected) in enumerate(findings, 1):
            priority = "High" if "error" in area.lower() or "Availability" in area else "Medium"
            lines.append(
                f"| PERF-{i:02d} | {priority} | {area} | {item} | {measured} | {expected} |"
            )
        lines += [
            "",
            "Copy these into QA/milestone4/day1/defect_tracker.md as DEF-M4-0xx with an owner.",
        ]
    else:
        lines.append("No findings: every endpoint and page is within its threshold.")
    report = "\n".join(lines) + "\n"

    print()
    print(report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"Report written to {args.report}")
    if args.json:
        Path(args.json).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

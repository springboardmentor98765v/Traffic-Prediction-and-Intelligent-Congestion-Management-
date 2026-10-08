"""Milestone 4 Day 6 — final regression pass + production stability sign-off.

Re-runs the Day 3 smoke test, the Day 4 full-system + Selenium UI tests and the Day 5
performance check
after the Day 5/6 fixes, compares them with the earlier runs, and watches the live
services for a while to confirm stability:

    python QA/milestone4/day6/final_regression.py --stability-minutes 10 \
        --report QA/milestone4/day6/final_regression_report.md

Regression = a check that PASSED on Day 4 and FAILS now, or an endpoint whose warm p95
got more than 50 % (and 200 ms) slower than on Day 5. Baselines are the JSON files the
earlier days wrote (day4/full_system_results.json, day5/performance_results.json); run
those with --json first. Without baselines the pass still runs, it just can't diff.

Sign-off = no FAIL in the functional suites, no regressions, no performance errors and
>= 99 % health-probe success during the stability window.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
M4 = HERE.parent
sys.path.insert(0, str(M4))
from live_common import HEALTH_PATHS, call, now_utc, service_urls  # noqa: E402

SUITES = [
    ("Smoke (Day 3 suite)", M4 / "day3" / "smoke_test_live.py", "smoke_results.json"),
    ("Full system (Day 4 suite)", M4 / "day4" / "full_system_test.py", "full_system_results.json"),
]
UI_SUITE = ("Selenium UI (Chrome)", M4 / "day4" / "selenium_ui_test.py", "selenium_ui_results.json")
PERF = M4 / "day5" / "performance_check.py"
BASE_FULL = M4 / "day4" / "full_system_results.json"
BASE_PERF = M4 / "day5" / "performance_results.json"


def run(script, *extra):
    print(f"\n=== {script.relative_to(M4)} {' '.join(extra)}")
    proc = subprocess.run(
        [sys.executable, str(script), *extra], capture_output=True, text=True, encoding="utf-8"
    )
    print(proc.stdout[-1500:])
    return proc.returncode


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def stability(urls, minutes, interval=30):
    """Probe every service's health path; returns {service: (ok, total, worst_ms)}."""
    stats = {name: [0, 0, 0.0] for name in HEALTH_PATHS}
    end = time.monotonic() + minutes * 60
    print(f"\n=== Stability window: {minutes} min, probe every {interval} s")
    while True:
        for name, path in HEALTH_PATHS.items():
            status, _, ms, _ = call(urls[name] + path, timeout=60)
            s = stats[name]
            s[1] += 1
            if status == 200:
                s[0] += 1
            s[2] = max(s[2], ms)
        if time.monotonic() >= end:
            break
        time.sleep(interval)
    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    parser.add_argument("--stability-minutes", type=float, default=10)
    args = parser.parse_args()
    urls = service_urls()

    out = HERE
    suite_rows = []
    suites = list(SUITES)
    try:
        import selenium  # noqa: F401

        suites.append(UI_SUITE)
    except ImportError:
        print("selenium not installed: skipping the UI suite (pip install selenium)")
    for label, script, json_name in suites:
        code = run(script, "--json", str(out / json_name))
        data = load(out / json_name) or {"rows": []}
        c = {k: sum(1 for r in data["rows"] if r["result"] == k) for k in ("PASS", "FAIL", "SKIP")}
        suite_rows.append((label, c, code))

    run(PERF, "--json", str(out / "performance_results.json"))
    perf = load(out / "performance_results.json") or {}

    # Functional regressions vs Day 4.
    regressions = []
    base_full = load(BASE_FULL)
    now_full = load(out / "full_system_results.json")
    if base_full and now_full:
        before = {(r["area"], r["check"]): r["result"] for r in base_full["rows"]}
        for r in now_full["rows"]:
            if before.get((r["area"], r["check"])) == "PASS" and r["result"] == "FAIL":
                regressions.append(
                    ("Functional", f"{r['area']} / {r['check']}", "PASS", f"FAIL ({r['actual']})")
                )
        fixed = [
            f"{r['area']} / {r['check']}"
            for r in now_full["rows"]
            if before.get((r["area"], r["check"])) == "FAIL" and r["result"] == "PASS"
        ]
    else:
        fixed = []

    # Performance regressions vs Day 5.
    base_perf = load(BASE_PERF)
    if base_perf and perf:
        before = {(r["service"], r["endpoint"]): r["p95"] for r in base_perf.get("latency", [])}
        for r in perf.get("latency", []):
            old, new = before.get((r["service"], r["endpoint"])), r["p95"]
            if old and new and new > old * 1.5 and new - old > 200:
                regressions.append(
                    (
                        "Performance",
                        f"{r['service']} {r['endpoint']}",
                        f"p95 {old:.0f} ms",
                        f"p95 {new:.0f} ms",
                    )
                )

    stab = stability(urls, args.stability_minutes)
    probes_ok = sum(s[0] for s in stab.values())
    probes = sum(s[1] for s in stab.values())
    uptime = 100.0 * probes_ok / probes if probes else 0.0

    perf_errors = [
        f for f in perf.get("findings", []) if "error" in f[0].lower() or f[0] == "Availability"
    ]
    functional_fail = sum(c["FAIL"] for _, c, _ in suite_rows)
    signed_off = functional_fail == 0 and not regressions and not perf_errors and uptime >= 99.0

    lines = [
        "# Milestone 4 Day 6 — Final Regression Report & Stability Sign-off",
        "",
        f"- Run: {now_utc()}",
        "- Targets: " + ", ".join(f"{k} `{v}`" for k, v in urls.items()),
        f"- Baselines: Day 4 {'found' if base_full else 'missing'}, "
        f"Day 5 {'found' if base_perf else 'missing'}",
        "",
        "## Sign-off: "
        + ("✅ STABLE — approved for final demo" if signed_off else "❌ NOT signed off"),
        "",
        "| Criterion | Result |",
        "| --- | --- |",
        f"| Functional suites: 0 FAIL | {functional_fail} FAIL |",
        f"| No regressions vs Day 4 / Day 5 | {len(regressions)} found |",
        f"| No API/availability errors under load | {len(perf_errors)} found |",
        f"| Health probes >= 99 % over {args.stability_minutes:g} min "
        f"| {uptime:.1f} % ({probes_ok}/{probes}) |",
        "",
        "## 1. Functional regression",
        "",
        "| Suite | PASS | FAIL | SKIP |",
        "| --- | --- | --- | --- |",
    ]
    lines += [
        f"| {label} | {c['PASS']} | {c['FAIL']} | {c['SKIP']} |" for label, c, _ in suite_rows
    ]
    if fixed:
        lines += ["", "Fixed since Day 4: " + "; ".join(fixed)]
    lines += [
        "",
        "Full tables: `smoke_results.json`, `full_system_results.json` in this folder.",
        "",
    ]
    lines += ["## 2. Regressions", ""]
    if regressions:
        lines += ["| Type | Item | Before | Now |", "| --- | --- | --- | --- |"]
        lines += [f"| {t} | {i} | {b} | {n} |" for t, i, b, n in regressions]
    else:
        lines.append("None." if (base_full or base_perf) else "No baselines to compare against.")
    lines += ["", "## 3. Performance (re-run)", ""]
    if perf.get("latency"):
        lines += ["| Service | Endpoint | p95 now (ms) | Limit |", "| --- | --- | --- | --- |"]
        lines += [
            f"| {r['service']} | {r['endpoint']} | {r['p95']:.0f} | {r['limit']:.0f} |"
            for r in perf["latency"]
            if r["p95"] is not None
        ]
    lines += [
        "",
        f"Open performance findings: {len(perf.get('findings', []))} "
        "(see `performance_results.json`).",
        "",
    ]
    lines += [
        "## 4. Stability window",
        "",
        "| Service | Probes OK | Worst response (ms) |",
        "| --- | --- | --- |",
    ]
    lines += [f"| {name} | {s[0]}/{s[1]} | {s[2]:.0f} |" for name, s in stab.items()]
    report = "\n".join(lines) + "\n"

    print("\n" + report)
    if args.report:
        Path(args.report).write_text(report, encoding="utf-8")
        print(f"Report written to {args.report}")
    return 0 if signed_off else 1


if __name__ == "__main__":
    sys.exit(main())

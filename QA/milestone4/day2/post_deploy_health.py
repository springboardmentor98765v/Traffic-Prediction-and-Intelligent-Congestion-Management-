"""Milestone 4 Day 2 — post-deploy health gate for the CI/CD deploy stage.

Polls every deployed service until it answers 200 or the timeout runs out:

    python QA/milestone4/day2/post_deploy_health.py --host <vm-ip-or-dns> [--timeout 180]
    python QA/milestone4/day2/post_deploy_health.py --scheme https --host api.example.com
    python QA/milestone4/day2/post_deploy_health.py --timeout 300
        --url backend=https://tv-team1-backend.onrender.com
        --url analytics=https://tv-team1-analytics.onrender.com
        --url ai=https://tv-team1-ai.onrender.com

With --url (Render / any per-service URL; one command line) the same checks run against
each service's own base URL instead of host:port.

Exits non-zero if any service is still unhealthy, which makes the deploy job fail and
triggers its rollback step. Stdlib only, so it runs on a bare GitHub runner.
The full functional smoke test is still QA/milestone3/day2/stack_smoke_test.py (Day 3).
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

# (service, port, path) — ports match docker-compose.prod.yml.
CHECKS = [
    ("backend", 8000, "/health"),
    ("analytics", 8001, "/"),
    ("ai", 8010, "/health"),
    # One real read through the gateway, not just a liveness probe.
    ("backend-live-traffic", 8000, "/api/v1/traffic/live"),
]


def probe(url, timeout=5):
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, OSError) as exc:
        return None, str(getattr(exc, "reason", exc)), 0.0
    return status, "", (time.perf_counter() - start) * 1000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        metavar="SERVICE=BASE_URL",
        help="per-service base URL (backend/analytics/ai); repeat for each service",
    )
    parser.add_argument("--scheme", default="http", choices=["http", "https"])
    parser.add_argument("--timeout", type=int, default=180, help="total seconds to wait")
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--json", help="also write results to this file")
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout
    if args.url:
        bases = dict(item.split("=", 1) for item in args.url)
        missing = {name.split("-")[0] for name, _, _ in CHECKS} - set(bases)
        if missing:
            parser.error(f"--url missing for: {', '.join(sorted(missing))}")
        pending = {name: bases[name.split("-")[0]].rstrip("/") + path for name, _, path in CHECKS}
    elif args.host:
        pending = {name: f"{args.scheme}://{args.host}:{port}{path}" for name, port, path in CHECKS}
    else:
        parser.error("give --host or --url")
    results = {}

    while pending:
        for name, url in list(pending.items()):
            status, error, ms = probe(url)
            results[name] = {"url": url, "status": status, "error": error, "ms": round(ms)}
            if status == 200:
                print(f"PASS {name:22} {url}  {ms:.0f} ms")
                del pending[name]
        if not pending or time.monotonic() >= deadline:
            break
        print(f"waiting on: {', '.join(pending)} ...")
        time.sleep(args.interval)

    for name in pending:
        r = results[name]
        print(f"FAIL {name:22} {r['url']}  status={r['status']} {r['error']}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)

    print(f"\n{len(CHECKS) - len(pending)}/{len(CHECKS)} services healthy")
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())

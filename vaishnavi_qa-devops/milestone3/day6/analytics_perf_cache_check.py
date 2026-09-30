"""Milestone 3 Day 6: Analytics caching + 4-week performance check.

1. Cold (cache flushed) vs warm (cached) latency, 5 runs each, per endpoint
2. Redis-down fallback: stop the Redis container, endpoints must still return 200
3. Query plans for the 4-week report / trend queries (index usage)

    python QA/milestone3/day6/analytics_perf_cache_check.py
Needs the dev stack up and Data loaded (analytics_setup.sh). Stops Redis briefly.
"""

import json
import statistics
import subprocess
import sys
import time
import urllib.request

AN = "http://127.0.0.1:8001"
REDIS = "trafficvision-redis-dev"
PG = "trafficvision-postgres-dev"
PATHS = {
    "trends R001 (4 wk)": "/analytics/trends?road_id=R001",
    "heatmap hour (4 wk)": "/analytics/heatmap?time_bucket=hour",
    "heatmap day (4 wk)": "/analytics/heatmap?time_bucket=day",
    "report all rows": "/analytics/reports?limit=50000",
}


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=False).stdout.strip()


def flush_cache():
    keys = sh("docker", "exec", REDIS, "redis-cli", "--scan", "--pattern", "analytics:*")
    for key in keys.split():
        sh("docker", "exec", REDIS, "redis-cli", "DEL", key)


RESETS = []


def timed(path, timeout=30):
    # One retry on a connection reset: the Windows Docker port proxy drops the
    # odd localhost connection (seen on both services, server logs show 200).
    for attempt in range(2):
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(AN + path, timeout=timeout) as resp:
                resp.read()
                return resp.status, (time.perf_counter() - start) * 1000
        except ConnectionResetError:
            RESETS.append(path)
            if attempt:
                raise


def latency():
    out = {}
    for name, path in PATHS.items():
        cold, warm = [], []
        for _ in range(5):
            flush_cache()
            cold.append(timed(path)[1])
            warm.append(timed(path)[1])
        out[name] = {
            "cold_median_ms": round(statistics.median(cold), 1),
            "cold_max_ms": round(max(cold), 1),
            "warm_median_ms": round(statistics.median(warm), 1),
            "pass_under_2s": max(cold) < 2000,
        }
    return out


def redis_down(budget_s=5):
    """Fallback must be both correct (200) and fast (< budget_s)."""
    sh("docker", "stop", REDIS)
    out = {}
    try:
        for name, path in PATHS.items():
            start = time.perf_counter()
            try:
                status, ms = timed(path, timeout=budget_s)
                out[name] = {"status": status, "ms": round(ms, 1), "pass": status == 200}
            except OSError:
                out[name] = {
                    "status": f"no response in {budget_s}s",
                    "ms": round((time.perf_counter() - start) * 1000, 1),
                    "pass": False,
                }
        return out
    finally:
        sh("docker", "start", REDIS)
        for _ in range(20):
            if sh("docker", "exec", REDIS, "redis-cli", "ping") == "PONG":
                break
            time.sleep(0.5)


def plans():
    queries = {
        "report R001 4 wk": "SELECT * FROM traffic_history WHERE road_id='R001' "
        "ORDER BY reading_timestamp, history_id LIMIT 10000",
        "trend R001 daily": "SELECT (reading_timestamp AT TIME ZONE 'Asia/Kolkata')::date d, "
        "avg(vehicle_count) FROM traffic_history WHERE road_id='R001' "
        "GROUP BY 1",
    }
    out = {}
    for name, q in queries.items():
        plan = sh(
            "docker",
            "exec",
            PG,
            "psql",
            "-tA",
            "-U",
            "traffic",
            "-d",
            "trafficvision",
            "-c",
            f"EXPLAIN (ANALYZE, FORMAT JSON) {q}",
        )
        root = json.loads(plan)[0]
        nodes, stack = [], [root["Plan"]]
        while stack:
            n = stack.pop()
            nodes.append(n["Node Type"] + (f" ({n['Index Name']})" if "Index Name" in n else ""))
            stack.extend(n.get("Plans", []))
        out[name] = {"exec_ms": root["Execution Time"], "nodes": nodes}
    return out


def main():
    report = {"latency": latency(), "redis_down": redis_down(), "plans": plans()}
    report["client_connection_resets_retried"] = len(RESETS)
    print(json.dumps(report, indent=2))
    ok = all(v["pass_under_2s"] for v in report["latency"].values()) and all(
        v["pass"] for v in report["redis_down"].values()
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

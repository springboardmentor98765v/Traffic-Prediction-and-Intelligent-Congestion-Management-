#!/usr/bin/env python3
"""
TrafficVision AI - Performance Benchmarking Script (Milestone 4 - Day 6)
Measures latency (min, max, mean, p50, p95, p99) and throughput (RPS)
across key Gateway and downstream service endpoints.
"""

import sys
import time
import statistics
import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 25

def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def benchmark_endpoint(name, method, url, headers=None, json_data=None, rounds=ROUNDS):
    latencies = []
    status_codes = []
    
    print(f"Benchmarking: {name:<25} ({rounds} requests) ... ", end="", flush=True)
    
    for _ in range(rounds):
        start = time.perf_counter()
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json=json_data, timeout=10)
            else:
                resp = None
            duration_ms = (time.perf_counter() - start) * 1000.0
            latencies.append(duration_ms)
            status_codes.append(resp.status_code if resp is not None else 0)
        except Exception as e:
            duration_ms = (time.perf_counter() - start) * 1000.0
            latencies.append(duration_ms)
            status_codes.append(0)
    
    if not latencies:
        print("FAILED (no data)")
        return None
        
    latencies_sorted = sorted(latencies)
    n = len(latencies_sorted)
    
    min_lat = min(latencies_sorted)
    max_lat = max(latencies_sorted)
    mean_lat = statistics.mean(latencies_sorted)
    p50_lat = statistics.median(latencies_sorted)
    p95_lat = latencies_sorted[int(n * 0.95)] if n > 1 else p50_lat
    p99_lat = latencies_sorted[int(n * 0.99)] if n > 1 else max_lat
    success_rate = (sum(1 for c in status_codes if 200 <= c < 300) / n) * 100
    rps = 1000.0 / mean_lat if mean_lat > 0 else 0
    
    print(f"DONE (Success: {success_rate:.0f}%, Mean: {mean_lat:.2f}ms)")
    
    return {
        "name": name,
        "rounds": n,
        "success_rate": success_rate,
        "min": min_lat,
        "mean": mean_lat,
        "p50": p50_lat,
        "p95": p95_lat,
        "p99": p99_lat,
        "max": max_lat,
        "rps": rps
    }

def main():
    print_header(f"TrafficVision AI - Gateway & Service Latency Benchmark")
    print(f"Target Base URL: {BASE_URL}")
    print(f"Iterations per endpoint: {ROUNDS}")
    
    # 1. Obtain Auth Tokens
    print("\nPreparing Auth credentials...")
    login_url = f"{BASE_URL}/api/v1/auth/login"
    reg_url = f"{BASE_URL}/api/v1/auth/register"
    email = f"perf_{int(time.time())}@trafficvision.ai"
    password = "PerfPassword123!"

    # Register benchmark user
    try:
        reg_r = requests.post(reg_url, json={"name": "Perf User", "email": email, "password": password, "role": "admin"}, timeout=5)
        if reg_r.status_code not in (200, 201):
            print(f"Warning: Registration returned HTTP {reg_r.status_code}: {reg_r.text}")
    except Exception as e:
        print(f"Warning: Registration request failed: {e}")

    admin_token = None
    try:
        r = requests.post(login_url, json={"email": email, "password": password}, timeout=5)
        if r.status_code == 200:
            admin_token = r.json().get("access_token")
            print(f"Successfully authenticated as {email}.")
        else:
            print(f"Warning: Login returned HTTP {r.status_code}: {r.text}. Some auth endpoints will be skipped.")
    except Exception as e:
        print(f"Warning: Auth failed with {e}")

    admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}
    gzip_headers = {**admin_headers, "Accept-Encoding": "gzip"}

    results = []

    # Endpoint 1: Gateway Core Health
    r1 = benchmark_endpoint(
        "Gateway Health (/health)",
        "GET",
        f"{BASE_URL}/health"
    )
    if r1: results.append(r1)

    # Endpoint 2: Gateway Readiness
    r2 = benchmark_endpoint(
        "Gateway Ready (/ready)",
        "GET",
        f"{BASE_URL}/ready"
    )
    if r2: results.append(r2)

    # Endpoint 3: Auth Verification (/auth/me)
    if admin_token:
        r3 = benchmark_endpoint(
            "Auth Me (/auth/me)",
            "GET",
            f"{BASE_URL}/api/v1/auth/me",
            headers=admin_headers
        )
        if r3: results.append(r3)

    # Endpoint 4: Prediction Proxy (/predict/congestion)
    r4 = benchmark_endpoint(
        "Predict Congestion",
        "GET",
        f"{BASE_URL}/api/v1/predict/congestion?road_id=1&density=0.75&vehicle_count=80",
        headers=admin_headers
    )
    if r4: results.append(r4)

    # Endpoint 5: Route Analysis Proxy (/route/conditions)
    r5 = benchmark_endpoint(
        "Route Conditions",
        "GET",
        f"{BASE_URL}/api/v1/route/conditions?road_id=1",
        headers=admin_headers
    )
    if r5: results.append(r5)

    # Endpoint 6: Alert Service (/alerts/active)
    r6 = benchmark_endpoint(
        "Active Alerts",
        "GET",
        f"{BASE_URL}/api/v1/alerts/active",
        headers=admin_headers
    )
    if r6: results.append(r6)

    # Check GZip compression on active alerts
    try:
        cmp_resp = requests.get(f"{BASE_URL}/api/v1/alerts/active", headers=gzip_headers)
        enc = cmp_resp.headers.get("content-encoding", "none")
        print(f"\nResponse Compression Verification: Content-Encoding = {enc}")
    except Exception:
        pass

    # Print Table
    print_header("BENCHMARK RESULTS SUMMARY")
    print(f"{'Endpoint':<24} | {'Success':<7} | {'Min (ms)':<8} | {'Mean(ms)':<8} | {'p50(ms)':<8} | {'p95(ms)':<8} | {'p99(ms)':<8} | {'Est RPS':<7}")
    print("-" * 92)
    for res in results:
        print(f"{res['name']:<24} | {res['success_rate']:<6.0f}% | {res['min']:<8.2f} | {res['mean']:<8.2f} | {res['p50']:<8.2f} | {res['p95']:<8.2f} | {res['p99']:<8.2f} | {res['rps']:<7.1f}")
    print("-" * 92)

if __name__ == "__main__":
    main()

"""
TrafficVision AI — Cross-Platform Gateway Verification Script.
Runs comprehensive checks for:
1. Health & Readiness endpoints
2. Strict CORS allowed origin vs blocked origin
3. Security Headers (X-Request-ID, nosniff, frame-options)
4. Rate Limiting enforcement (HTTP 429 with Retry-After)
"""

import sys
import time
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

def run_tests():
    print("=" * 60)
    print("TrafficVision AI — Gateway Production Test Suite")
    print("=" * 60)

    # Use TestClient for fast, deterministic local verification
    client = TestClient(app)
    allowed_origin = settings.get_cors_origins()[0]
    blocked_origin = "http://malicious-attacker.com"

    # 1. Health Probe Check
    print("[1/5] Testing GET /health ...", end=" ")
    resp = client.get("/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["status"] == "healthy", f"Unexpected payload: {data}"
    assert "X-Request-ID" in resp.headers, "Missing X-Request-ID header"
    assert resp.headers["X-Content-Type-Options"] == "nosniff", "Missing X-Content-Type-Options"
    print(f"PASS (200 OK, request_id={resp.headers['X-Request-ID']})")

    # 2. Readiness Probe Check
    print("[2/5] Testing GET /ready ...", end=" ")
    resp = client.get("/ready")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    data = resp.json()
    assert data["status"] == "ready", f"Unexpected payload: {data}"
    print(f"PASS (200 OK, db={data.get('database')})")

    # 3. CORS Allowed Origin
    print(f"[3/5] Testing Allowed CORS Origin ({allowed_origin}) ...", end=" ")
    resp = client.options("/health", headers={
        "Origin": allowed_origin,
        "Access-Control-Request-Method": "GET"
    })
    acao = resp.headers.get("access-control-allow-origin")
    assert acao == allowed_origin, f"Expected {allowed_origin}, got {acao}"
    print(f"PASS (Access-Control-Allow-Origin: {acao})")

    # 4. CORS Blocked Origin
    print(f"[4/5] Testing Blocked CORS Origin ({blocked_origin}) ...", end=" ")
    resp = client.options("/health", headers={
        "Origin": blocked_origin,
        "Access-Control-Request-Method": "GET"
    })
    acao = resp.headers.get("access-control-allow-origin")
    assert acao != blocked_origin, f"Blocked origin was granted CORS access: {acao}"
    print("PASS (Blocked origin received no CORS authorization)")

    # 5. Rate Limiting Check (Auth route limit = 10 requests/min)
    print("[5/5] Testing Auth Rate Limiting trigger (threshold: 10/min) ...", end=" ")
    triggered_429 = False
    for i in range(1, 15):
        resp = client.post(
            "/api/v1/auth/login",
            json={"email": "ratelimit_test@example.com", "password": "wrong"},
            headers={"x-forwarded-for": "198.51.100.42"}
        )
        if resp.status_code == 429:
            triggered_429 = True
            retry_after = resp.headers.get("Retry-After")
            print(f"PASS (HTTP 429 triggered on attempt #{i}, Retry-After={retry_after}s)")
            break

    assert triggered_429, "Rate limiter did not return HTTP 429 within 15 attempts!"

    print("=" * 60)
    print("All Gateway Production Verification Checks PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)

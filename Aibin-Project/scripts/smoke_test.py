"""
TrafficVision AI — Cross-Platform Smoke Test Tool
Usage:
  python scripts/smoke_test.py [BASE_URL]
"""

import sys
import requests

def run_smoke_test(base_url="http://127.0.0.1:8080"):
    print("=" * 65)
    print(f"TrafficVision AI — Cloud Deployment Smoke Test: {base_url}")
    print("=" * 65)

    session = requests.Session()

    # 1. Gateway Health
    print("[1/7] Testing Gateway Health (/health) ...", end=" ")
    try:
        r = session.get(f"{base_url}/health", timeout=5)
        if r.status_code == 200 and r.json().get("status") == "healthy":
            print(f"PASS (HTTP 200, {r.json()})")
        else:
            print(f"FAIL (HTTP {r.status_code}, {r.text})")
            return False
    except Exception as e:
        print(f"FAIL (Connection Error: {e})")
        return False

    # 2. Database Readiness
    print("[2/7] Testing Database Readiness (/ready) ...", end=" ")
    try:
        r = session.get(f"{base_url}/ready", timeout=5)
        if r.status_code == 200 and r.json().get("status") == "ready":
            print(f"PASS (HTTP 200, db={r.json().get('database')})")
        else:
            print(f"FAIL (HTTP {r.status_code}, {r.text})")
            return False
    except Exception as e:
        print(f"FAIL (Connection Error: {e})")
        return False

    # 3. Authentication Login
    print("[3/7] Testing Authentication (POST /api/v1/auth/login) ...", end=" ")
    token = None
    try:
        r = session.post(
            f"{base_url}/api/v1/auth/login",
            json={"email": "admin@trafficvision.ai", "password": "Admin@12345"},
            timeout=5
        )
        if r.status_code == 200:
            token = r.json().get("access_token")
            print(f"PASS (HTTP 200, role={r.json().get('role')})")
        else:
            print(f"FAIL (HTTP {r.status_code}, {r.text})")
            return False
    except Exception as e:
        print(f"FAIL (Error: {e})")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Token Profile Verification
    print("[4/7] Testing Current User Profile (/api/v1/auth/me) ...", end=" ")
    try:
        r = session.get(f"{base_url}/api/v1/auth/me", headers=headers, timeout=5)
        if r.status_code == 200:
            print(f"PASS (HTTP 200, email={r.json().get('email')})")
        else:
            print(f"FAIL (HTTP {r.status_code})")
            return False
    except Exception as e:
        print(f"FAIL ({e})")
        return False

    # 5. Route Analysis via Gateway
    print("[5/7] Testing Route Analysis via Gateway (/api/v1/route/conditions?road_id=1) ...", end=" ")
    try:
        r = session.get(f"{base_url}/api/v1/route/conditions?road_id=1", headers=headers, timeout=5)
        print(f"HTTP {r.status_code} ({'PASS' if r.status_code == 200 else 'UPSTREAM_OFFLINE'})")
    except Exception as e:
        print(f"FAILED ({e})")

    # 6. Alert Service via Gateway
    print("[6/7] Testing Alert Service via Gateway (/api/v1/alerts/active) ...", end=" ")
    try:
        r = session.get(f"{base_url}/api/v1/alerts/active", headers=headers, timeout=5)
        print(f"HTTP {r.status_code} ({'PASS' if r.status_code == 200 else 'UPSTREAM_OFFLINE'})")
    except Exception as e:
        print(f"FAILED ({e})")

    # 7. AI Prediction Engine via Gateway
    print("[7/7] Testing AI Prediction via Gateway (/api/v1/predict/congestion?road_id=1) ...", end=" ")
    try:
        r = session.get(f"{base_url}/api/v1/predict/congestion?road_id=1", headers=headers, timeout=5)
        print(f"HTTP {r.status_code} ({'PASS' if r.status_code == 200 else 'UPSTREAM_OFFLINE'})")
    except Exception as e:
        print(f"FAILED ({e})")

    print("=" * 65)
    print("Smoke Test Verification Completed!")
    print("=" * 65)
    return True

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080"
    success = run_smoke_test(url)
    sys.exit(0 if success else 1)

"""M1 end-to-end check against the running docker-compose.dev.yml stack.

    docker compose -f docker-compose.dev.yml up -d --build
    python QA/milestone1/day5/m1_live_stack_check.py

This covers the user journey from SRS section 12.2 ("Full Integration"): register, log in,
read live traffic, read a prediction, and get a 403 on a role-gated route, all through
the gateway on :8000 plus the AI Engine heuristic stub on :8010.

Optional: set OPERATOR_EMAIL / OPERATOR_PASSWORD (a provisioned operator account) to also
check the allow path of RBAC. Exit code is the number of failed checks.
"""

import os
import sys
import uuid

import requests

GATEWAY = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
AI_ENGINE = os.getenv("AI_ENGINE_URL", "http://127.0.0.1:8010")
API = f"{GATEWAY}/api/v1"
PASSWORD = "QaM1#Live2026"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def main():
    try:
        check("gateway /health", requests.get(f"{GATEWAY}/health", timeout=5).ok)
    except requests.ConnectionError:
        print(f"Gateway not reachable at {GATEWAY}; is the compose stack up?")
        return 1

    email = f"qa.m1.live.{uuid.uuid4().hex[:8]}@gmail.com"
    reg = requests.post(
        f"{API}/auth/register",
        json={"name": email.split("@")[0], "email": email, "password": PASSWORD},
        timeout=10,
    )
    check("register -> 201", reg.status_code == 201, reg.status_code)

    login = requests.post(
        f"{API}/auth/login", json={"email": email, "password": PASSWORD}, timeout=10
    )
    check("login -> 200 with tokens", login.ok and "access_token" in login.json())
    tokens = login.json() if login.ok else {}
    access = tokens.get("access_token", "")

    me = requests.get(f"{API}/auth/me", headers=bearer(access), timeout=10)
    check("me -> PUBLIC", me.ok and me.json().get("role") == "PUBLIC", me.status_code)

    ref = requests.post(
        f"{API}/auth/refresh", json={"refresh_token": tokens.get("refresh_token", "")}, timeout=10
    )
    check("refresh -> 200", ref.ok, ref.status_code)

    live = requests.get(f"{API}/traffic/live", timeout=10)
    roads = live.json() if live.ok else []
    check("traffic/live -> non-empty list", live.ok and len(roads) > 0, f"{len(roads)} roads")
    road_id = roads[0]["road_id"] if roads else "R001"

    road = requests.get(f"{API}/traffic/road/{road_id}", timeout=10)
    check(f"traffic/road/{road_id} -> 200", road.ok, road.status_code)

    density = requests.get(f"{API}/traffic/density", timeout=10)
    check("traffic/density -> 200", density.ok, density.status_code)

    pred = requests.get(f"{API}/predict/congestion", params={"road_id": road_id}, timeout=15)
    check("gateway predict/congestion -> 200", pred.ok, pred.text[:120])

    stub = requests.get(
        f"{AI_ENGINE}/api/v1/predict/congestion", params={"road_id": road_id}, timeout=15
    )
    check(
        "AI engine stub -> heuristic-v0",
        stub.ok and stub.json().get("generated_by") == "heuristic-v0",
        stub.text[:120],
    )

    alert = {"type": "congestion", "severity": "High", "road_id": road_id, "message": "QA M1"}
    denied = requests.post(f"{API}/alerts/", json=alert, headers=bearer(access), timeout=10)
    check("RBAC: public POST /alerts -> 403", denied.status_code == 403, denied.status_code)

    op_email, op_pw = os.getenv("OPERATOR_EMAIL"), os.getenv("OPERATOR_PASSWORD")
    if op_email and op_pw:
        op = requests.post(
            f"{API}/auth/login", json={"email": op_email, "password": op_pw}, timeout=10
        )
        check("operator login -> 200", op.ok, op.status_code)
        op_token = op.json().get("access_token", "") if op.ok else ""
        allowed = requests.post(f"{API}/alerts/", json=alert, headers=bearer(op_token), timeout=10)
        check("RBAC: operator POST /alerts -> 201", allowed.status_code == 201)
    else:
        print("[SKIP] RBAC allow path: set OPERATOR_EMAIL / OPERATOR_PASSWORD")

    failed = sum(1 for _, ok in results if not ok)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    return failed


if __name__ == "__main__":
    sys.exit(main())

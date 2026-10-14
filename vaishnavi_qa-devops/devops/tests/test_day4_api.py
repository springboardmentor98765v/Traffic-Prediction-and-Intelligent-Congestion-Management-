"""M1/M2 regression: auth + RBAC and traffic monitoring, against the /api/v1 contract.

Runs in-process (TestClient), no Docker needed: the root conftest.py points
DATABASE_URL at a throwaway SQLite file, and the traffic service falls back to its
built-in sample data when the traffic tables aren't there.

Rewritten 2026-09-25 (DEF-M3-001): the original called the pre-M2 routes
(/api/auth/*, /api/traffic/*, /api/auth/admin) and RD-101 road ids.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "QaPass#2026"


@pytest.fixture(scope="module")
def client():
    # Context manager runs the startup hook, which creates the tables.
    with TestClient(app) as c:
        yield c


def new_email():
    # Registration only accepts allow-listed domains (app/schemas/user.py).
    return f"qa.m1.{uuid.uuid4().hex[:8]}@gmail.com"


def register_and_login(client, role=None):
    email = new_email()
    body = {"name": email.split("@")[0], "email": email, "password": PASSWORD}
    if role:
        body["role"] = role
    register = client.post("/api/v1/auth/register", json=body)
    assert register.status_code == 201, register.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.status_code == 200, login.text
    return login.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_register_login_me_refresh(client):
    tokens = register_and_login(client)
    assert {"access_token", "refresh_token", "role"} <= tokens.keys()

    me = client.get("/api/v1/auth/me", headers=auth(tokens["access_token"]))
    assert me.status_code == 200, me.text
    assert me.json()["role"] == "PUBLIC"

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 200, refresh.text
    assert "access_token" in refresh.json()


def test_auth_rejects_bad_credentials_and_missing_token(client):
    email = new_email()
    client.post(
        "/api/v1/auth/register",
        json={"name": email.split("@")[0], "email": email, "password": PASSWORD},
    )
    wrong = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong"})
    assert wrong.status_code == 401
    assert client.get("/api/v1/auth/me").status_code in (401, 403)


def test_rbac_self_registration_cannot_grant_admin(client):
    # Public sign-up must always create a PUBLIC user, whatever role is requested.
    tokens = register_and_login(client, role="admin")
    assert tokens["role"] == "PUBLIC"
    me = client.get("/api/v1/auth/me", headers=auth(tokens["access_token"]))
    assert me.json()["role"] == "PUBLIC"


def test_registration_rejects_unsupported_domain(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "blocked", "email": "blocked@example.com", "password": PASSWORD},
    )
    assert resp.status_code == 422


def test_traffic_endpoints(client):
    live = client.get("/api/v1/traffic/live")
    assert live.status_code == 200, live.text
    roads = live.json()
    assert isinstance(roads, list) and roads
    assert {"road_id", "vehicle_count", "density", "congestion_level"} <= roads[0].keys()

    road = client.get("/api/v1/traffic/road/R001")
    assert road.status_code == 200, road.text
    assert road.json()["road_id"] == "R001"
    assert road.json()["history"]

    density = client.get("/api/v1/traffic/density")
    assert density.status_code == 200, density.text
    assert {"total_roads", "average_density"} <= density.json().keys()

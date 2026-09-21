import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.environ["DATABASE_URL"] = f"sqlite:///{ROOT / 'test.db'}"
os.environ["JWT_SECRET"] = "test-secret"
sys.path.insert(0, str(ROOT / "services" / "auth"))

from fastapi.testclient import TestClient
from app.main import Base, engine, app

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def create_operator():
    return client.post("/api/v1/auth/register", json={"name": "Operator", "email": "operator@example.com", "password": "password123", "role": "traffic_operator"})


def test_register_login_refresh_and_me():
    registered = create_operator()
    assert registered.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": "operator@example.com", "password": "password123"})
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["role"] == "traffic_operator"
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200 and me.json()["name"] == "Operator"
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200 and "access_token" in refreshed.json()


def test_rbac_denies_non_admin():
    assert create_operator().status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": "operator@example.com", "password": "password123"}).json()
    denied = client.get("/api/v1/admin/health", headers={"Authorization": f"Bearer {login['access_token']}"})
    assert denied.status_code == 403

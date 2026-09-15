import pytest
from fastapi.testclient import TestClient
import uuid

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.database.connection import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


def test_register_and_login():
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Integration Tester",
            "email": unique_email,
            "password": "Password123!",
            "role": "operator"
        }
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["email"] == unique_email
    assert reg_data["role"] == "operator"
    assert "user_id" in reg_data

    # Duplicate registration should fail
    dup_res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Duplicate Tester",
            "email": unique_email,
            "password": "Password123!",
            "role": "operator"
        }
    )
    assert dup_res.status_code == 400

    # Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_email,
            "password": "Password123!"
        }
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["role"] == "operator"

    # Profile via /me
    token = token_data["access_token"]
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email


def test_login_invalid_credentials():
    res = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrong"
        }
    )
    assert res.status_code == 401


def test_rbac_admin_vs_public():
    admin_email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    public_email = f"public_{uuid.uuid4().hex[:8]}@example.com"

    # Register admin
    client.post(
        "/api/v1/auth/register",
        json={"name": "Admin", "email": admin_email, "password": "AdminPassword123!", "role": "admin"}
    )
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": admin_email, "password": "AdminPassword123!"}
    ).json()

    # Register public
    client.post(
        "/api/v1/auth/register",
        json={"name": "Public", "email": public_email, "password": "PublicPassword123!", "role": "public"}
    )
    public_login = client.post(
        "/api/v1/auth/login",
        json={"email": public_email, "password": "PublicPassword123!"}
    ).json()

    # Admin accessing /users -> 200
    res_admin = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_login['access_token']}"}
    )
    assert res_admin.status_code == 200
    assert isinstance(res_admin.json(), list)

    # Public accessing /users -> 403 Forbidden
    res_public = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {public_login['access_token']}"}
    )
    assert res_public.status_code == 403

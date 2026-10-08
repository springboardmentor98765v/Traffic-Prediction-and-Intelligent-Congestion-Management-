"""Shared fixtures for the Milestone 1 QA suite (Intern 5).

Runs in-process with FastAPI's TestClient, so no Docker is needed. The root conftest.py
puts the backend on sys.path and points DATABASE_URL at a throwaway SQLite file.

Admin and Operator accounts can't be created through /auth/register (public sign-up
always creates a PUBLIC user), so the fixtures insert them straight into the users table,
the same way an administrator would provision them.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.user import User
from app.security.password import hash_password
from m1_helpers import PASSWORD, new_email


@pytest.fixture(scope="session")
def client():
    # The context manager runs the lifespan hook, which creates the tables.
    with TestClient(app) as c:
        yield c


def _login(client, email, password=PASSWORD):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _provision(role):
    email = new_email(f"qa.m1.{role}")
    db = SessionLocal()
    try:
        db.add(
            User(
                id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                username=email.split("@")[0],
                email=email,
                password_hash=hash_password(PASSWORD),
                role=role,
            )
        )
        db.commit()
    finally:
        db.close()
    return email


@pytest.fixture
def public_user(client):
    email = new_email()
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": email.split("@")[0], "email": email, "password": PASSWORD},
    )
    assert resp.status_code == 201, resp.text
    return {"email": email, **_login(client, email)}


@pytest.fixture
def operator_user(client):
    email = _provision("operator")
    return {"email": email, **_login(client, email)}


@pytest.fixture
def admin_user(client):
    email = _provision("admin")
    return {"email": email, **_login(client, email)}

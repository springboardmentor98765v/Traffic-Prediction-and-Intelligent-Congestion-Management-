import uuid

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_optimize_route(client):
    email = f"qa-route-{uuid.uuid4().hex[:8]}@gmail.com"
    registration = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": "securepassword123"},
    )
    assert registration.status_code == 201, registration.text

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "securepassword123"},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/v1/route/optimize?origin=11.9416,79.8083&destination=11.9350,79.8100",
        headers=headers,
    )

    assert response.status_code == 200
    res_data = response.json()
    assert "distance_km" in res_data

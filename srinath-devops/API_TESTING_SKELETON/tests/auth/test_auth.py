import os
import requests
import uuid

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_register():
    test_email = f"api_test_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "name": "Test User",
        "email": test_email,
        "password": "TestPassword123!",
        "role": "public"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=payload
    )

    assert response.status_code in [200, 201]
    data = response.json()
    assert "user_id" in data
    assert data["email"] == test_email


def test_login():
    test_email = f"api_test_{uuid.uuid4().hex[:8]}@example.com"
    # Register first
    requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "name": "Login Tester",
            "email": test_email,
            "password": "TestPassword123!",
            "role": "operator"
        }
    )

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={
            "email": test_email,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "operator"


def test_login_invalid_password():
    payload = {
        "email": "testuser@example.com",
        "password": "WrongPassword!"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=payload
    )

    assert response.status_code in [400, 401, 403]


def test_login_unknown_email():
    payload = {
        "email": f"unknown_{uuid.uuid4().hex[:8]}@example.com",
        "password": "AnyPassword123!"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=payload
    )

    assert response.status_code in [400, 401, 403]


def test_current_user_without_token():
    response = requests.get(
        f"{BASE_URL}/api/v1/auth/me"
    )

    assert response.status_code in [401, 403]

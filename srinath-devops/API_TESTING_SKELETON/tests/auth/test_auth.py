import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_register():
    payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Test@123",
        "role": "Public/Commuter"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json=payload
    )

    assert response.status_code in [200, 201]


def test_login():
    payload = {
        "email": "testuser@example.com",
        "password": "Test@123"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=payload
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert "role" in data


def test_login_invalid_password():
    payload = {
        "email": "testuser@example.com",
        "password": "WrongPassword"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=payload
    )

    assert response.status_code in [400, 401, 403]


def test_login_unknown_email():
    payload = {
        "email": "unknown@example.com",
        "password": "Test@123"
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

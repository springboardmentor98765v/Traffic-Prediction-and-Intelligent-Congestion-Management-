"""
Tests for authentication endpoints (register, login, refresh, me).
"""
import pytest
from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    response = client.post("/api/v1/auth/register", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "secretpassword",
        "role": "traffic_operator"
    })
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data

def test_register_duplicate_email(client: TestClient):
    payload = {
        "name": "Jane Doe",
        "email": "jane2@example.com",
        "password": "secretpassword",
        "role": "traffic_operator"
    }
    response1 = client.post("/api/v1/auth/register", json=payload)
    assert response1.status_code == 201
    
    response2 = client.post("/api/v1/auth/register", json=payload)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"

def test_login_success(client: TestClient):
    client.post("/api/v1/auth/register", json={
        "name": "Jane Doe",
        "email": "jane3@example.com",
        "password": "secretpassword",
        "role": "traffic_operator"
    })
    
    response = client.post("/api/v1/auth/login", json={
        "email": "jane3@example.com",
        "password": "secretpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "traffic_operator"

def test_login_wrong_password(client: TestClient):
    client.post("/api/v1/auth/register", json={
        "name": "Jane Doe",
        "email": "jane4@example.com",
        "password": "secretpassword",
        "role": "traffic_operator"
    })
    
    response = client.post("/api/v1/auth/login", json={
        "email": "jane4@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

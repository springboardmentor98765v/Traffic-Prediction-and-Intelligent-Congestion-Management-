"""
Tests for Role-Based Access Control (RBAC) and Gateway proxies.
"""
import pytest
from fastapi.testclient import TestClient

def get_token_for_role(client: TestClient, role: str) -> str:
    email = f"test_{role}@example.com"
    client.post("/api/v1/auth/register", json={
        "name": f"Test {role}",
        "email": email,
        "password": "secretpassword",
        "role": role
    })
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "secretpassword"
    })
    return response.json()["access_token"]

def test_rbac_no_token(client: TestClient):
    response = client.get("/api/v1/traffic/road/1")
    assert response.status_code in [401, 403]

def test_rbac_wrong_role(client: TestClient):
    token = get_token_for_role(client, "public")
    response = client.get("/api/v1/traffic/road/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Operation not permitted" in response.json()["detail"]

def test_rbac_correct_role(client: TestClient):
    token = get_token_for_role(client, "admin")
    response = client.get("/api/v1/traffic/road/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    data = response.json()
    if isinstance(data, dict) and "note" in data:
        assert data["note"] == "traffic service not yet available, this is mock data"
    else:
        assert isinstance(data, list)

def test_prediction_gateway_access(client: TestClient):
    token = get_token_for_role(client, "public")
    response = client.get("/api/v1/predict/congestion?road_id=1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "predicted_level" in response.json()

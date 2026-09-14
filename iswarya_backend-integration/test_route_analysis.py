from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_optimize_route():
    # 1. Register a test user (or use existing test credentials)
    client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test_optimize@example.com",
        "password": "securepassword123",
        "role": "user"
    })

    # 2. Log in to get the access token
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test_optimize@example.com",
        "password": "securepassword123"
    })
    token = login_response.json().get("access_token")

    # 3. Pass the token in the Authorization header for the optimize route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/v1/route/optimize?origin=11.9416,79.8083&destination=11.9350,79.8100",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "route_id" in data
    assert "distance_km" in data
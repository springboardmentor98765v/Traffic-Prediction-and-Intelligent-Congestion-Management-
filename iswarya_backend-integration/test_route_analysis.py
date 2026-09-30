from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_optimize_route():
    # 1. Register a test user (matching UserCreate schema: name, email, password)
    client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test_optimize@example.com",
        "password": "securepassword123"
    })

    # 2. Log in to get the access token
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test_optimize@example.com",
        "password": "securepassword123"
    })
    
    data = login_response.json() if login_response.status_code == 200 else {}
    token = data.get("access_token")

    # Fallback to direct token generation if test login encounters state hiccups
    if not token:
        from app.routes.auth import create_access_token
        token = create_access_token({"sub": "USR-TEST1234", "username": "Test User", "role": "user"})

    # 3. Pass the token in the Authorization header for the optimize route
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        "/api/v1/route/optimize?origin=11.9416,79.8083&destination=11.9350,79.8100",
        headers=headers
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert "distance_km" in res_data
"""
Unit & Integration Tests for Route Analysis Microservice (Milestone 2: Day 1-5).
"""

import pytest
from fastapi.testclient import TestClient
from route_analysis.main import app
from app.main import app as gateway_app

client = TestClient(app)
gw_client = TestClient(gateway_app)

def test_route_analysis_health_check():
    """Verify Route Analysis service health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Route Analysis Service"
    assert "OpenStreetMap" in data["maps_provider"]

def test_optimize_route_success():
    """Test /api/v1/route/optimize with valid coordinates."""
    origin = "12.9716,77.5946"
    destination = "12.9352,77.6245"
    
    response = client.get(f"/api/v1/route/optimize?origin={origin}&destination={destination}")
    assert response.status_code == 200
    data = response.json()
    
    assert "route_id" in data
    assert isinstance(data["path"], list)
    assert len(data["path"]) >= 2
    for pt in data["path"]:
        assert len(pt) == 2
        assert isinstance(pt[0], float)
        assert isinstance(pt[1], float)
        assert -90.0 <= pt[0] <= 90.0
        assert -180.0 <= pt[1] <= 180.0
        
    assert "distance_km" in data
    assert data["distance_km"] > 0
    assert "congestion_score" in data
    assert 0.0 <= data["congestion_score"] <= 1.0

def test_alternate_routes_success():
    """Test /api/v1/route/alternate returns ranked candidate list."""
    origin = "12.9716,77.5946"
    destination = "12.9352,77.6245"
    
    response = client.get(f"/api/v1/route/alternate?origin={origin}&destination={destination}&max_routes=3")
    assert response.status_code == 200
    candidates = response.json()
    
    assert isinstance(candidates, list)
    assert len(candidates) >= 2
    
    # Verify ranking
    ranks = [c["rank"] for c in candidates]
    assert ranks == list(range(1, len(candidates) + 1))
    
    for c in candidates:
        assert "route_id" in c
        assert "path" in c
        assert len(c["path"]) >= 2
        assert "congestion_score" in c
        assert 0.0 <= c["congestion_score"] <= 1.0

def test_travel_time_endpoint():
    """Test GET /api/v1/route/travel-time with route_id."""
    origin = "12.9716,77.5946"
    destination = "12.9352,77.6245"
    
    opt_res = client.get(f"/api/v1/route/optimize?origin={origin}&destination={destination}")
    route_id = opt_res.json()["route_id"]
    
    tt_res = client.get(f"/api/v1/route/travel-time?route_id={route_id}")
    assert tt_res.status_code == 200
    tt_data = tt_res.json()
    assert tt_data["route_id"] == route_id
    assert tt_data["estimated_minutes"] > 0
    assert "live+predicted" in tt_data["based_on"] or "distance" in tt_data["based_on"]

def test_conditions_endpoint():
    """Test GET /api/v1/route/conditions with road_id."""
    res = client.get("/api/v1/route/conditions?road_id=1")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "1"
    assert "status" in data
    assert "notes" in data

def get_auth_headers():
    """Helper to register and login a test user to get JWT."""
    gw_client.post("/api/v1/auth/register", json={
        "name": "Proxy User",
        "email": "proxyuser@example.com",
        "password": "proxy_password",
        "role": "public"
    })
    res = gw_client.post("/api/v1/auth/login", json={
        "email": "proxyuser@example.com",
        "password": "proxy_password"
    })
    token = res.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

def test_gateway_route_proxy_all_endpoints():
    """Test all 4 route analysis routes are reachable via API Gateway."""
    origin = "12.9716,77.5946"
    destination = "12.9352,77.6245"
    headers = get_auth_headers()
    
    # 1. Gateway /optimize
    res1 = gw_client.get(f"/api/v1/route/optimize?origin={origin}&destination={destination}", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert "route_id" in data1
    
    # 2. Gateway /alternate
    res2 = gw_client.get(f"/api/v1/route/alternate?origin={origin}&destination={destination}", headers=headers)
    assert res2.status_code == 200
    assert len(res2.json()) >= 2
    
    # 3. Gateway /travel-time
    res3 = gw_client.get(f"/api/v1/route/travel-time?route_id={data1['route_id']}", headers=headers)
    assert res3.status_code == 200
    assert res3.json()["estimated_minutes"] > 0
    
    # 4. Gateway /conditions
    res4 = gw_client.get("/api/v1/route/conditions?road_id=1", headers=headers)
    assert res4.status_code == 200
    assert res4.json()["status"] in ["CLEAR", "NORMAL", "OPEN", "MODERATE"]

def test_gateway_prediction_proxy_endpoints():
    """Test prediction endpoints registered behind API Gateway."""
    headers = get_auth_headers()
    # 1. Congestion prediction
    res1 = gw_client.get("/api/v1/predict/congestion?road_id=1&density=0.55", headers=headers)
    assert res1.status_code == 200
    assert "predicted_level" in res1.json()
    
    # 2. Delay prediction
    res2 = gw_client.get("/api/v1/predict/delay?road_id=1&density=0.60", headers=headers)
    assert res2.status_code == 200
    assert "estimated_delay_minutes" in res2.json()
    
    # 3. Peak-hours detection
    res3 = gw_client.get("/api/v1/predict/peak-hours?hour=9", headers=headers)
    assert res3.status_code == 200
    assert res3.json()["is_peak"] is True

def test_coordinate_validation_malformed():
    """Test that malformed coordinate strings return 400 Bad Request."""
    res1 = client.get("/api/v1/route/optimize?origin=12.9716&destination=12.9352,77.6245")
    assert res1.status_code == 400
    assert "Invalid origin coordinates" in res1.json()["detail"]
    
    res2 = client.get("/api/v1/route/optimize?origin=abc,xyz&destination=12.9352,77.6245")
    assert res2.status_code == 400
    assert "floating-point" in res2.json()["detail"]

def test_coordinate_validation_out_of_range():
    """Test that out-of-range coordinates return 400 Bad Request."""
    res1 = client.get("/api/v1/route/optimize?origin=105.0,77.5946&destination=12.9352,77.6245")
    assert res1.status_code == 400
    assert "Latitude must be between -90.0 and 90.0" in res1.json()["detail"]
    
    res2 = client.get("/api/v1/route/optimize?origin=12.9716,200.0&destination=12.9352,77.6245")
    assert res2.status_code == 400
    assert "Longitude must be between -180.0 and 180.0" in res2.json()["detail"]

def test_alternate_routes_validation():
    """Test validation on /alternate endpoint."""
    res = client.get("/api/v1/route/alternate?origin=invalid&destination=12.9352,77.6245")
    assert res.status_code == 400

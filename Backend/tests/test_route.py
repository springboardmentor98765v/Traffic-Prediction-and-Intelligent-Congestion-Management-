import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_route_optimize_basic():
    res = client.get("/api/v1/route/optimize?origin=R001&destination=R002")
    assert res.status_code == 200
    data = res.json()
    assert "route_id" in data
    assert "path" in data
    assert len(data["path"]) >= 2
    assert "distance_km" in data
    assert data["distance_km"] > 0
    assert "congestion_score" in data
    assert data["congestion_score"] > 0
    assert "summary" in data


def test_route_optimize_coordinates():
    res = client.get("/api/v1/route/optimize?origin=12.9756,77.6066&destination=12.9249,77.6740")
    assert res.status_code == 200
    data = res.json()
    assert len(data["path"]) >= 2
    assert data["distance_km"] > 0


def test_route_alternate_ranking():
    res = client.get("/api/v1/route/alternate?origin=R001&destination=R004")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Verify ranking
    ranks = [r["rank"] for r in data]
    assert ranks == list(range(1, len(data) + 1))

    # Verify congestion-aware scoring ascending order
    scores = [r["congestion_score"] for r in data]
    assert scores == sorted(scores)

    for item in data:
        assert "route_id" in item
        assert "path" in item
        assert "distance_km" in item
        assert "recommendation_reason" in item


def test_route_travel_time():
    # First optimize to register route
    opt_res = client.get("/api/v1/route/optimize?origin=R001&destination=R003")
    route_id = opt_res.json()["route_id"]

    res = client.get(f"/api/v1/route/travel-time?route_id={route_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["route_id"] == route_id
    assert data["estimated_minutes"] > 0
    assert data["based_on"] == "live+predicted"


def test_route_conditions_get():
    res = client.get("/api/v1/route/conditions?road_id=R001")
    assert res.status_code == 200
    data = res.json()
    assert data["road_id"] == "R001"
    assert data["status"] in ["OPEN", "CONSTRUCTION", "CLOSED", "HAZARD"]
    assert "notes" in data


def test_route_conditions_update_rbac():
    # 1. Unauthenticated attempt -> 401
    res_unauth = client.post(
        "/api/v1/route/conditions",
        json={"road_id": "R001", "status": "CONSTRUCTION", "notes": "Road widening work"}
    )
    assert res_unauth.status_code == 401

    # 2. Register admin user & login
    admin_email = "admin_route_test@trafficvision.ai"
    client.post("/api/v1/auth/register", json={
        "name": "Route Admin",
        "email": admin_email,
        "password": "Password123!",
        "role": "admin"
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": admin_email,
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Authorized update -> 200
    res_auth = client.post(
        "/api/v1/route/conditions",
        json={"road_id": "R001", "status": "CONSTRUCTION", "notes": "Road repair in progress"},
        headers=headers
    )
    assert res_auth.status_code == 200
    updated = res_auth.json()
    assert updated["road_id"] == "R001"
    assert updated["status"] == "CONSTRUCTION"
    assert "Road repair" in updated["notes"]

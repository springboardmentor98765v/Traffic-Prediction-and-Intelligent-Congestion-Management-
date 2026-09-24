import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def get_auth_header(role: str = "public", prefix: str = "alerts_test"):
    uid = str(uuid.uuid4())[:8]
    email = f"{prefix}_{role}_{uid}@trafficvision.ai"
    password = "Password123!"

    client.post("/api/v1/auth/register", json={
        "name": f"{role.capitalize()} User",
        "email": email,
        "password": password,
        "role": role
    })

    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_alert_internal():
    unique_road = f"R_TEST_{str(uuid.uuid4())[:6]}"
    res = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "high",
            "road_id": unique_road,
            "message": "Heavy congestion on test corridor",
            "target_role": "public"
        }
    )
    assert res.status_code == 201
    data = res.json()
    assert "alert_id" in data
    assert data["type"] == "congestion"
    assert data["severity"] == "high"
    assert data["road_id"] == unique_road.upper()
    assert data["status"] == "created"


def test_alert_noise_deduplication():
    unique_road = f"R_DEDUP_{str(uuid.uuid4())[:6]}"
    # First alert creation
    res1 = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "medium",
            "road_id": unique_road,
            "message": "Initial congestion detected"
        }
    )
    assert res1.status_code == 201
    alert_id_1 = res1.json()["alert_id"]

    # Second alert creation within time window for the same road & type
    res2 = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "high",
            "road_id": unique_road,
            "message": "Congestion worsening on corridor"
        }
    )
    assert res2.status_code == 201
    alert_id_2 = res2.json()["alert_id"]

    # Should deduplicate to the same alert record
    assert alert_id_1 == alert_id_2
    assert res2.json()["message"] == "Congestion worsening on corridor"


def test_rbac_alert_visibility():
    admin_headers = get_auth_header(role="admin", prefix="adm_vis")
    public_headers = get_auth_header(role="public", prefix="pub_vis")

    internal_road = f"R_INTERNAL_{str(uuid.uuid4())[:6]}"
    public_road = f"R_PUBLIC_{str(uuid.uuid4())[:6]}"

    # Create internal operational alert (target_role: operator)
    client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "low",
            "road_id": internal_road,
            "message": "Internal maintenance monitor alert",
            "target_role": "operator"
        }
    )

    # Create public safety alert (target_role: public)
    client.post(
        "/api/v1/alerts",
        json={
            "type": "accident",
            "severity": "critical",
            "road_id": public_road,
            "message": "Multi-car collision reported",
            "target_role": "public"
        }
    )

    # 1. Admin query -> sees both
    admin_res = client.get("/api/v1/alerts/my", headers=admin_headers)
    assert admin_res.status_code == 200
    admin_roads = [a["road_id"] for a in admin_res.json()]
    assert internal_road.upper() in admin_roads
    assert public_road.upper() in admin_roads

    # 2. Public query -> sees public safety alert, internal is excluded
    public_res = client.get("/api/v1/alerts/my", headers=public_headers)
    assert public_res.status_code == 200
    public_roads = [a["road_id"] for a in public_res.json()]
    assert public_road.upper() in public_roads
    assert internal_road.upper() not in public_roads


def test_mark_alert_read():
    user_headers = get_auth_header(role="public", prefix="read_test")

    # Create an alert
    road_id = f"R_READ_{str(uuid.uuid4())[:6]}"
    create_res = client.post(
        "/api/v1/alerts",
        json={
            "type": "accident",
            "severity": "high",
            "road_id": road_id,
            "message": "Vehicle breakdown",
            "target_role": "public"
        }
    )
    alert_id = create_res.json()["alert_id"]

    # Mark as read
    read_res = client.post(f"/api/v1/alerts/{alert_id}/read", headers=user_headers)
    assert read_res.status_code == 200
    assert read_res.json()["read"] is True

    # Verify that it now shows read=True in get_my_alerts
    my_res = client.get("/api/v1/alerts/my", headers=user_headers)
    match = [a for a in my_res.json() if a["alert_id"] == alert_id]
    assert len(match) == 1
    assert match[0]["read"] is True


def test_active_alerts_endpoint():
    res = client.get("/api/v1/alerts/active")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    for a in data:
        assert a["is_active"] is True
        assert "alert_id" in a
        assert "type" in a
        assert "severity" in a


def test_alerts_poll_endpoint():
    user_headers = get_auth_header(role="public", prefix="poll_test")
    res = client.get("/api/v1/alerts/poll", headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert "timestamp" in data
    assert "unread_count" in data
    assert "active_count" in data
    assert isinstance(data["alerts"], list)

    # Test 'since' parameter
    past_iso = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    res_since = client.get(f"/api/v1/alerts/poll?since={past_iso}", headers=user_headers)
    assert res_since.status_code == 200
    data_since = res_since.json()
    assert "alerts" in data_since


def test_evaluate_triggers_endpoint():
    res = client.post("/api/v1/alerts/evaluate-triggers")
    assert res.status_code == 200
    data = res.json()
    assert "triggered_count" in data
    assert "alerts" in data
    assert "details" in data
    assert "status" in data["details"]

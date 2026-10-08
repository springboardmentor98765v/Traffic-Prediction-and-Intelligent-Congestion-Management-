import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routes.alerts import ALERT_SERVICE_KEY
from app.routes.auth import create_access_token


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def token(role):
    return create_access_token({"sub": f"qa-{role}", "username": f"qa-{role}", "role": role})


def create_alert(client, role, severity, alert_type):
    return client.post(
        "/api/v1/alerts/",
        headers={"Authorization": f"Bearer {token(role)}"},
        json={
            "type": alert_type,
            "severity": severity,
            "road_id": "R004",
            "message": f"QA {severity} {alert_type}",
        },
    )


def test_public_users_do_not_see_high_accident_alerts(client):
    accident = create_alert(client, "admin", "High", "accident")
    congestion = create_alert(client, "admin", "High", "congestion")
    assert accident.status_code == congestion.status_code == 201

    response = client.get(
        "/api/v1/alerts/my",
        headers={"Authorization": f"Bearer {token('user')}"},
    )
    assert response.status_code == 200
    ids = {alert["alert_id"] for alert in response.json()}
    assert accident.json()["alert_id"] not in ids
    assert congestion.json()["alert_id"] in ids


def test_public_users_cannot_mark_shared_alerts_read(client):
    created = create_alert(client, "admin", "High", "congestion")
    assert created.status_code == 201

    response = client.patch(
        f"/api/v1/alerts/{created.json()['alert_id']}/read",
        headers={"Authorization": f"Bearer {token('user')}"},
    )
    assert response.status_code == 403


def test_alert_timestamps_include_utc_offset(client):
    created = create_alert(client, "admin", "High", "congestion")
    assert created.status_code == 201

    response = client.get(
        "/api/v1/alerts/my",
        headers={"Authorization": f"Bearer {token('admin')}"},
    )
    alert = next(item for item in response.json() if item["alert_id"] == created.json()["alert_id"])
    assert alert["created_at"].endswith("Z") or "+" in alert["created_at"][10:]


def test_producer_service_key_can_create_alert(client):
    response = client.post(
        "/api/v1/alerts/",
        headers={"X-Alert-Service-Key": ALERT_SERVICE_KEY},
        json={
            "type": "congestion",
            "severity": "High",
            "road_id": "R001",
            "message": "QA producer-key authorization",
        },
    )
    assert response.status_code == 201, response.text

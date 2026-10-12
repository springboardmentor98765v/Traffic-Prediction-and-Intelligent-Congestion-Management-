import uuid

from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.database.connection import SessionLocal
from app.database.models import Role, User
from app.main import app
from app.route.maps import maps_service

client = TestClient(app)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

TEST_PASSWORD = "Test@12345"


def create_test_user(role_name):
    db = SessionLocal()

    try:
        role = db.query(Role).filter(Role.name == role_name).first()

        assert role is not None

        email = f"test-{role_name}-{uuid.uuid4().hex[:8]}@example.com"

        user = User(
            name=f"Test {role_name.title()}",
            email=email,
            password_hash=pwd_context.hash(TEST_PASSWORD),
            role_id=role.id,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return email
    finally:
        db.close()


def get_token(role_name):
    email = create_test_user(role_name)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def fake_get_route(
    origin_lat,
    origin_lng,
    destination_lat,
    destination_lng,
    alternatives=False,
):
    routes = [
        {
            "distance": 5000,
            "duration": 600,
            "geometry": {
                "coordinates": [
                    [origin_lng, origin_lat],
                    [
                        (origin_lng + destination_lng) / 2,
                        (origin_lat + destination_lat) / 2,
                    ],
                    [destination_lng, destination_lat],
                ]
            },
        }
    ]

    if alternatives:
        routes.append(
            {
                "distance": 6500,
                "duration": 540,
                "geometry": {
                    "coordinates": [
                        [origin_lng, origin_lat],
                        [
                            (origin_lng + destination_lng) / 2,
                            (origin_lat + destination_lat) / 2 + 0.01,
                        ],
                        [destination_lng, destination_lat],
                    ]
                },
            }
        )

    return {
        "code": "Ok",
        "routes": routes,
    }


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_operator_login():
    token = get_token("operator")

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_operator_me():
    token = get_token("operator")

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "operator"


def test_traffic_record_requires_authentication():
    response = client.post(
        "/api/v1/traffic/record",
        params={
            "road_id": 1,
            "vehicle_count": 50,
            "density": 0.70,
            "congestion_level": "MEDIUM",
        },
    )

    assert response.status_code == 401


def test_public_user_cannot_record_traffic():
    token = get_token("public")

    response = client.post(
        "/api/v1/traffic/record",
        params={
            "road_id": 1,
            "vehicle_count": 50,
            "density": 0.70,
            "congestion_level": "MEDIUM",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_operator_can_record_traffic():
    token = get_token("operator")

    response = client.post(
        "/api/v1/traffic/record",
        params={
            "road_id": 1,
            "vehicle_count": 50,
            "density": 0.70,
            "congestion_level": "MEDIUM",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Traffic record created"
    assert "record_id" in data


def test_traffic_history():
    response = client.get(
        "/api/v1/traffic/history",
        params={
            "road_id": 1,
            "start": "2026-01-01T00:00:00",
            "end": "2027-01-01T00:00:00",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_traffic_history_invalid_range():
    response = client.get(
        "/api/v1/traffic/history",
        params={
            "road_id": 1,
            "start": "2027-01-01T00:00:00",
            "end": "2026-01-01T00:00:00",
        },
    )

    assert response.status_code == 400


def test_traffic_aggregate_hour():
    response = client.get(
        "/api/v1/traffic/aggregate",
        params={
            "road_id": 1,
            "granularity": "hour",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "road_id" in data[0]
        assert "period" in data[0]
        assert "average_vehicle_count" in data[0]
        assert "average_density" in data[0]


def test_traffic_aggregate_day():
    response = client.get(
        "/api/v1/traffic/aggregate",
        params={
            "road_id": 1,
            "granularity": "day",
        },
    )

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_traffic_aggregate_invalid_granularity():
    response = client.get(
        "/api/v1/traffic/aggregate",
        params={
            "road_id": 1,
            "granularity": "month",
        },
    )

    assert response.status_code == 400


def test_operator_can_get_congestion_prediction():
    token = get_token("operator")

    response = client.get(
        "/api/v1/predict/congestion",
        params={
            "road_id": 1,
            "time": "2026-09-11T08:00:00",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["predicted_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]
    assert 0 <= data["confidence"] <= 1
    assert data["model_version"] == "random-forest-v1"


def test_prediction_unknown_road():
    token = get_token("operator")

    response = client.get(
        "/api/v1/predict/congestion",
        params={
            "road_id": 9999,
            "time": "2026-09-11T08:00:00",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404


def test_peak_hours_prediction():
    token = get_token("operator")

    response = client.get(
        "/api/v1/predict/peak-hours",
        params={
            "road_id": 1,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert isinstance(data["peak_windows"], list)


def test_delay_prediction():
    token = get_token("operator")

    response = client.get(
        "/api/v1/predict/delay",
        params={
            "road_id": 1,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["estimated_delay_minutes"] >= 0
    assert 0 <= data["confidence"] <= 1


def test_route_optimize(monkeypatch):
    monkeypatch.setattr(
        maps_service,
        "get_route",
        fake_get_route,
    )

    response = client.get(
        "/api/v1/route/optimize",
        params={
            "origin_lat": 13.0827,
            "origin_lng": 80.2707,
            "destination_lat": 13.0674,
            "destination_lng": 80.2376,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route_id"].startswith("route-")
    assert isinstance(data["path"], list)
    assert data["distance_km"] > 0
    assert data["duration_minutes"] > 0
    assert 0 <= data["congestion_score"] <= 1


def test_route_alternate(monkeypatch):
    monkeypatch.setattr(
        maps_service,
        "get_route",
        fake_get_route,
    )

    response = client.get(
        "/api/v1/route/alternate",
        params={
            "origin_lat": 13.0827,
            "origin_lng": 80.2707,
            "destination_lat": 13.0674,
            "destination_lng": 80.2376,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    ranks = [route["rank"] for route in data]

    assert ranks == list(range(1, len(data) + 1))

    for route in data:
        assert route["route_id"].startswith("route-")
        assert route["distance_km"] > 0
        assert route["duration_minutes"] > 0
        assert 0 <= route["congestion_score"] <= 1


def test_route_travel_time(monkeypatch):
    monkeypatch.setattr(
        maps_service,
        "get_route",
        fake_get_route,
    )

    optimize_response = client.get(
        "/api/v1/route/optimize",
        params={
            "origin_lat": 13.0827,
            "origin_lng": 80.2707,
            "destination_lat": 13.0674,
            "destination_lng": 80.2376,
        },
    )

    assert optimize_response.status_code == 200

    route_id = optimize_response.json()["route_id"]

    response = client.get(
        "/api/v1/route/travel-time",
        params={
            "route_id": route_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["route_id"] == route_id
    assert data["estimated_minutes"] > 0
    assert data["based_on"] == "live+predicted"


def test_route_travel_time_unknown_route():
    response = client.get(
        "/api/v1/route/travel-time",
        params={
            "route_id": "route-does-not-exist",
        },
    )

    assert response.status_code == 404


def test_road_condition():
    response = client.get(
        "/api/v1/route/conditions",
        params={
            "road_id": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["status"] == "NORMAL"
    assert data["notes"] == "Traffic flowing normally"


def test_unknown_road_condition():
    response = client.get(
        "/api/v1/route/conditions",
        params={
            "road_id": 9999,
        },
    )

    assert response.status_code == 404


def test_openapi_contains_m2_endpoints():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    expected_paths = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/me",
        "/api/v1/traffic/history",
        "/api/v1/traffic/aggregate",
        "/api/v1/traffic/record",
        "/api/v1/predict/congestion",
        "/api/v1/predict/peak-hours",
        "/api/v1/predict/delay",
        "/api/v1/route/optimize",
        "/api/v1/route/alternate",
        "/api/v1/route/travel-time",
        "/api/v1/route/conditions",
    ]

    for path in expected_paths:
        assert path in paths

def test_m3_create_alert():
    response = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "high",
            "road_id": 1,
            "message": "M3 automated test alert",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "alert_id" in data
    assert isinstance(data["alert_id"], int)


def test_m3_my_alerts_role_scoped():
    token = get_token("operator")

    create_response = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "high",
            "road_id": 1,
            "message": "M3 role scoped test alert",
        },
    )

    assert create_response.status_code == 201

    alert_id = create_response.json()["alert_id"]

    response = client.get(
        "/api/v1/alerts/my",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert any(alert["alert_id"] == alert_id for alert in data)


def test_m3_mark_alert_read():
    token = get_token("operator")

    create_response = client.post(
        "/api/v1/alerts",
        json={
            "type": "congestion",
            "severity": "high",
            "road_id": 1,
            "message": "M3 mark read test alert",
        },
    )

    assert create_response.status_code == 201

    alert_id = create_response.json()["alert_id"]

    response = client.post(
        f"/api/v1/alerts/{alert_id}/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["alert_id"] == alert_id
    assert data["read"] is True


def test_m3_operator_active_alerts():
    token = get_token("operator")

    response = client.get(
        "/api/v1/alerts/active",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    if data:
        assert "alert_id" in data[0]
        assert "type" in data[0]
        assert "severity" in data[0]
        assert "road_id" in data[0]
        assert "message" in data[0]
        assert "read" in data[0]
        assert "created_at" in data[0]


def test_m3_public_cannot_get_active_alerts():
    token = get_token("public")

    response = client.get(
        "/api/v1/alerts/active",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_m3_trends_day():
    response = client.get(
        "/api/v1/analytics/trends",
        params={
            "road_id": 1,
            "range": "day",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["range"] == "day"
    assert isinstance(data["data"], list)

    if data["data"]:
        assert "timestamp" in data["data"][0]
        assert "vehicle_count" in data["data"][0]
        assert "density" in data["data"][0]
        assert "congestion_level" in data["data"][0]


def test_m3_trends_week():
    response = client.get(
        "/api/v1/analytics/trends",
        params={
            "road_id": 1,
            "range": "week",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["range"] == "week"
    assert isinstance(data["data"], list)


def test_m3_trends_invalid_range():
    response = client.get(
        "/api/v1/analytics/trends",
        params={
            "road_id": 1,
            "range": "year",
        },
    )

    assert response.status_code == 400


def test_m3_heatmap():
    response = client.get(
        "/api/v1/analytics/heatmap",
        params={
            "range": "day",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["range"] == "day"
    assert isinstance(data["data"], list)

    if data["data"]:
        assert "road_id" in data["data"][0]
        assert "timestamp" in data["data"][0]
        assert "density" in data["data"][0]
        assert "vehicle_count" in data["data"][0]
        assert "congestion_level" in data["data"][0]


def test_m3_reports_json():
    response = client.get(
        "/api/v1/analytics/reports",
        params={
            "range": "day",
            "format": "json",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["range"] == "day"
    assert isinstance(data["data"], list)


def test_m3_reports_csv():
    response = client.get(
        "/api/v1/analytics/reports",
        params={
            "range": "day",
            "format": "csv",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "road_id" in response.text
    assert "timestamp" in response.text
    assert "vehicle_count" in response.text
    assert "density" in response.text
    assert "congestion_level" in response.text


def test_m3_reports_invalid_format():
    response = client.get(
        "/api/v1/analytics/reports",
        params={
            "range": "day",
            "format": "xml",
        },
    )

    assert response.status_code == 400


def test_openapi_contains_m3_endpoints():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    expected_paths = [
        "/api/v1/alerts",
        "/api/v1/alerts/my",
        "/api/v1/alerts/{alert_id}/read",
        "/api/v1/alerts/active",
        "/api/v1/analytics/trends",
        "/api/v1/analytics/heatmap",
        "/api/v1/analytics/reports",
    ]

    for path in expected_paths:
        assert path in paths

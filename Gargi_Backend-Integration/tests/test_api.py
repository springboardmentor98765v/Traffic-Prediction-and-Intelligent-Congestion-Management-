from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_operator_token():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "operator@test.com",
            "password": "operator123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_prediction_requires_authentication():
    response = client.get("/api/v1/predict/congestion?road_id=1")

    assert response.status_code == 401


def test_traffic_live_requires_authentication():
    response = client.get("/api/v1/traffic/live")

    assert response.status_code == 401


def test_traffic_road_requires_authentication():
    response = client.get("/api/v1/traffic/road/1")

    assert response.status_code == 401


def test_traffic_density_requires_authentication():
    response = client.get("/api/v1/traffic/density")

    assert response.status_code == 401


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


def test_operator_login():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "operator@test.com",
            "password": "operator123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "operator"


def test_operator_me():
    token = get_operator_token()

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == 2
    assert data["name"] == "Operator User"
    assert data["role"] == "operator"


def test_operator_can_access_live_traffic():
    token = get_operator_token()

    response = client.get(
        "/api/v1/traffic/live",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_operator_can_access_road_traffic():
    token = get_operator_token()

    response = client.get(
        "/api/v1/traffic/road/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["road_id"] == 1
    assert data["name"] == "Anna Salai"
    assert "history" in data


def test_operator_can_access_density():
    token = get_operator_token()

    response = client.get(
        "/api/v1/traffic/density",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_operator_can_get_prediction():
    token = get_operator_token()

    response = client.get(
        "/api/v1/predict/congestion",
        params={"road_id": 1},
        headers={"Authorization": f"Bearer {token}"},
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
    assert data["generated_by"] == "heuristic-v0"


def test_prediction_unknown_road():
    token = get_operator_token()

    response = client.get(
        "/api/v1/predict/congestion",
        params={"road_id": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_openapi_contains_all_required_endpoints():
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    expected_paths = [
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/me",
        "/api/v1/traffic/live",
        "/api/v1/traffic/road/{road_id}",
        "/api/v1/traffic/density",
        "/api/v1/traffic/record",
        "/api/v1/predict/congestion",
    ]

    for path in expected_paths:
        assert path in paths

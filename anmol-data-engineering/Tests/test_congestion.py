from fastapi.testclient import TestClient
from Api.traffic_api import app


def get_congestion_level(density):

    if density >= 0.85:
        return "SEVERE"
    elif density >= 0.65:
        return "HIGH"
    elif density >= 0.40:
        return "MEDIUM"
    else:
        return "LOW"


def test_low_congestion():

    assert get_congestion_level(0.20) == "LOW"


def test_medium_congestion():

    assert get_congestion_level(0.40) == "MEDIUM"
    assert get_congestion_level(0.64) == "MEDIUM"


def test_high_congestion():

    assert get_congestion_level(0.65) == "HIGH"
    assert get_congestion_level(0.84) == "HIGH"


def test_severe_congestion():

    assert get_congestion_level(0.85) == "SEVERE"
    assert get_congestion_level(1.00) == "SEVERE"


# M2 Day 6 - Historical traffic API check
def test_historical_traffic_api():

    client = TestClient(app)

    response = client.get("/traffic/history/1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if response.json():
        record = response.json()[0]

        assert "reading_id" in record
        assert "road_id" in record
        assert "sensor_id" in record
        assert "timestamp" in record
        assert "vehicle_count" in record
        assert "density" in record
        assert "congestion_level" in record


# M2 Day 6 - Road-condition API check
def test_road_conditions_api():

    client = TestClient(app)

    response = client.get("/traffic/conditions/1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    if response.json():
        condition = response.json()[0]

        assert "condition_id" in condition
        assert "road_id" in condition
        assert "condition_status" in condition
        assert "description" in condition
        assert "start_time" in condition
        assert "end_time" in condition
        assert "created_at" in condition

        assert condition["condition_status"] in [
            "OPEN",
            "CONSTRUCTION",
            "CLOSED"
        ]
import requests


BASE_URL = "http://localhost:8000"


def test_traffic_monitoring():
    response = requests.get(f"{BASE_URL}/traffic")

    assert response.status_code == 200


def test_traffic_data_response():
    response = requests.get(f"{BASE_URL}/traffic")

    assert response.status_code == 200
    assert response.json() is not None


def test_traffic_endpoint_not_found():
    response = requests.get(f"{BASE_URL}/invalid-traffic-endpoint")

    assert response.status_code == 404

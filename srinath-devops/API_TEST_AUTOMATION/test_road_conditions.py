import os
import pytest
import requests

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
CONDITIONS_URL = os.getenv("ROUTE_SERVICE_URL", f"{BASE_URL}/api/v1/route/conditions")


@pytest.fixture(scope="module")
def public_auth_headers():
    """Mock/token for Public user."""
    token = os.getenv("PUBLIC_AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture(scope="module")
def operator_auth_headers():
    """Mock/token for Operator user."""
    token = os.getenv("OPERATOR_AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.mark.conditions
def test_get_road_condition_public(public_auth_headers):
    """TC-ROUT-007: Verify Public users can view active road conditions."""
    params = {"road_id": "road_1"}
    try:
        response = requests.get(CONDITIONS_URL, params=params, headers=public_auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Road conditions service unreachable at {CONDITIONS_URL}")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    data = response.json()
    assert "road_id" in data


@pytest.mark.rbac
def test_mutate_road_condition_public_forbidden(public_auth_headers):
    """TC-SEC-001: Verify Public users are forbidden (403) from creating/updating road conditions."""
    payload = {
        "road_id": "road_1",
        "condition": "Closed",
        "description": "Unauthorized closure attempt"
    }
    try:
        response = requests.post(CONDITIONS_URL, json=payload, headers=public_auth_headers, timeout=5)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Road conditions service unreachable at {CONDITIONS_URL}")

    assert response.status_code in [401, 403], f"Expected 401/403 for unauthorized mutation, got {response.status_code}"

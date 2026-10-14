"""M1 gateway contract and frontend wiring checks.

Gateway: every frozen M1 route is registered and documented in Swagger (SRS 7.1-7.3).
Frontend: static checks on Intern 4's pages, which have no test runner of their own.
They confirm the pages call the right gateway routes and gate each dashboard by role.
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
FRONTEND = REPO / "Front-end(m-3) (1)" / "Front-end"

FROZEN_ROUTES = [
    ("post", "/api/v1/auth/register"),
    ("post", "/api/v1/auth/login"),
    ("post", "/api/v1/auth/refresh"),
    ("get", "/api/v1/auth/me"),
    ("get", "/api/v1/traffic/live"),
    ("get", "/api/v1/traffic/road/{road_id}"),
    ("get", "/api/v1/traffic/density"),
    ("get", "/api/v1/predict/congestion"),
]


# ---------- Gateway ----------


def test_tc_gw_01_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200 and resp.json()["status"] == "ok"


@pytest.mark.parametrize("method, path", FROZEN_ROUTES)
def test_tc_gw_02_frozen_route_in_openapi(client, method, path):
    spec = client.get("/openapi.json").json()
    assert path in spec["paths"], f"{path} missing from OpenAPI"
    assert method in spec["paths"][path]


def test_tc_gw_03_swagger_ui_served(client):
    assert client.get("/docs").status_code == 200


def test_tc_gw_04_unknown_route_404(client):
    assert client.get("/api/v1/does-not-exist").status_code == 404


# ---------- Frontend (static) ----------


def read(name):
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_tc_ui_01_api_client_targets_gateway_v1():
    assert "BASE_URL: 'http://127.0.0.1:8000/api/v1'" in read("api.js")


@pytest.mark.parametrize(
    "route",
    [
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
        "/traffic/live",
        "/traffic/density",
        "/traffic/road/",
        "/predict/congestion",
    ],
)
def test_tc_ui_02_api_client_calls_m1_routes(route):
    assert route in read("api.js")


def test_tc_ui_03_login_redirects_by_server_role():
    login = read("Login.html")
    assert "authAPI.login(" in login
    assert "AuthManager.getDashboardUrl(data.role" in login


@pytest.mark.parametrize(
    "page, roles",
    [
        ("admin dashboard.html", ["ADMIN"]),
        ("operator dashboard.html", ["OPERATOR", "ADMIN"]),
        ("public dashboard.html", ["PUBLIC", "OPERATOR", "ADMIN", "USER"]),
    ],
)
def test_tc_ui_04_dashboards_are_role_gated(page, roles):
    match = re.search(r"AuthManager\.guardPage\(\[(.*?)\]\)", read(page))
    assert match, f"{page} has no role guard"
    found = re.findall(r"'([A-Z_]+)'", match.group(1))
    assert found == roles


def test_tc_ui_05_role_to_dashboard_mapping():
    api = read("api.js")
    assert "if (r === 'ADMIN') return 'admin dashboard.html';" in api
    assert "return 'operator dashboard.html';" in api
    assert "return 'public dashboard.html';" in api


def test_tc_ui_06_expired_token_triggers_silent_refresh():
    api = read("api.js")
    assert "response.status === 401 && AuthManager.getRefreshToken()" in api

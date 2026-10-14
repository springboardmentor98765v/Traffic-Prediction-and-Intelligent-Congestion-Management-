"""M1 role-based access control (FR-02) for Admin / Traffic Operator / Public.

The only role-gated routes in the gateway are the alert routes (POST /api/v1/alerts/ and
PATCH /api/v1/alerts/{id}/read). The M1 traffic and prediction routes are open to
everyone (DEF-M1-003), so these tests check role enforcement on the routes that have it,
plus the role claims every protected route depends on.
"""

import jwt
import pytest

from app.security.config import ALGORITHM, SECRET_KEY
from m1_helpers import PASSWORD, bearer, new_email

ALERT = {"type": "congestion", "severity": "High", "road_id": "R006", "message": "QA M1 RBAC"}


def test_tc_rbac_01_self_registration_cannot_request_admin(client):
    email = new_email()
    body = {"name": email.split("@")[0], "email": email, "password": PASSWORD, "role": "admin"}
    assert client.post("/api/v1/auth/register", json=body).status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert login.json()["role"] == "PUBLIC"


@pytest.mark.parametrize(
    "fixture, claim, me_role",
    [
        ("public_user", "user", "PUBLIC"),
        ("operator_user", "operator", "OPERATOR"),
        ("admin_user", "admin", "ADMIN"),
    ],
)
def test_tc_rbac_02_jwt_and_me_carry_the_right_role(client, request, fixture, claim, me_role):
    user = request.getfixturevalue(fixture)
    claims = jwt.decode(user["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["role"] == claim
    me = client.get("/api/v1/auth/me", headers=bearer(user["access_token"]))
    assert me.json()["role"] == me_role


def test_tc_rbac_03_public_cannot_create_alert(client, public_user):
    resp = client.post("/api/v1/alerts/", json=ALERT, headers=bearer(public_user["access_token"]))
    assert resp.status_code == 403


def test_tc_rbac_04_anonymous_cannot_create_alert(client):
    assert client.post("/api/v1/alerts/", json=ALERT).status_code in (401, 403)


@pytest.mark.parametrize("fixture", ["operator_user", "admin_user"])
def test_tc_rbac_05_operator_and_admin_can_create_alert(client, request, fixture):
    user = request.getfixturevalue(fixture)
    resp = client.post("/api/v1/alerts/", json=ALERT, headers=bearer(user["access_token"]))
    assert resp.status_code == 201, resp.text


def test_tc_rbac_06_public_cannot_mark_alert_read(client, operator_user, public_user):
    created = client.post(
        "/api/v1/alerts/", json=ALERT, headers=bearer(operator_user["access_token"])
    ).json()
    resp = client.patch(
        f"/api/v1/alerts/{created['alert_id']}/read", headers=bearer(public_user["access_token"])
    )
    assert resp.status_code == 403


def test_tc_rbac_07_operator_can_mark_alert_read(client, operator_user):
    created = client.post(
        "/api/v1/alerts/", json=ALERT, headers=bearer(operator_user["access_token"])
    ).json()
    resp = client.patch(
        f"/api/v1/alerts/{created['alert_id']}/read",
        headers=bearer(operator_user["access_token"]),
    )
    assert resp.status_code == 200, resp.text


def test_tc_rbac_08_forged_admin_token_rejected(client):
    forged = jwt.encode(
        {"sub": "USR-FORGED", "role": "admin", "token_type": "access"},
        "not-the-server-secret-key-0000000",
        algorithm=ALGORITHM,
    )
    resp = client.post("/api/v1/alerts/", json=ALERT, headers=bearer(forged))
    assert resp.status_code in (401, 403)
    assert client.get("/api/v1/auth/me", headers=bearer(forged)).status_code == 401


@pytest.mark.xfail(
    strict=True,
    reason="DEF-M1-004: login returns 'PUBLIC' for users but lower-case 'admin'/'operator'",
)
def test_tc_rbac_09_login_role_format_is_consistent(client, public_user, admin_user):
    assert public_user["role"].isupper() and admin_user["role"].isupper()


@pytest.mark.xfail(
    strict=True,
    reason="DEF-M1-003: M1 traffic/prediction routes do not require a token",
)
def test_tc_rbac_10_monitoring_routes_require_authentication(client):
    assert client.get("/api/v1/traffic/live").status_code in (401, 403)

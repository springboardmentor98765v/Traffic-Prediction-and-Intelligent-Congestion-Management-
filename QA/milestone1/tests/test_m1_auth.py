"""M1 Authentication service (Intern 1) against the frozen contract, SRS section 7.1.

Test IDs match QA/milestone1/day3/m1_test_cases.md.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.security.config import ALGORITHM, SECRET_KEY
from m1_helpers import PASSWORD, bearer, new_email


def register(client, email=None, name=None, password=PASSWORD):
    email = email or new_email()
    body = {"name": name if name is not None else email.split("@")[0], "email": email}
    body["password"] = password
    return client.post("/api/v1/auth/register", json=body)


# ---------- Register ----------


def test_tc_auth_01_register_valid_user_returns_201_and_user_id(client):
    resp = register(client)
    assert resp.status_code == 201, resp.text
    assert resp.json()["user_id"]


def test_tc_auth_02_register_duplicate_email_rejected(client):
    email = new_email()
    assert register(client, email).status_code == 201
    dup = register(client, email, name=email.split("@")[0] + "x")
    assert dup.status_code == 409, dup.text


def test_tc_auth_03_register_unsupported_domain_rejected(client):
    assert register(client, "someone@example.com").status_code == 422


def test_tc_auth_04_register_malformed_email_rejected(client):
    assert register(client, "not-an-email").status_code == 422


@pytest.mark.xfail(
    strict=True,
    reason="DEF-M1-001: /auth/register accepts an empty password and empty name (returns 201)",
)
def test_tc_auth_05_register_empty_password_rejected(client):
    assert register(client, password="").status_code == 422


@pytest.mark.xfail(
    strict=True,
    reason="DEF-M1-001: /auth/register accepts an empty password and empty name (returns 201)",
)
def test_tc_auth_06_register_empty_name_rejected(client):
    assert register(client, name="").status_code == 422


# ---------- Login ----------


def test_tc_auth_07_login_valid_returns_access_refresh_and_role(client, public_user):
    assert {"access_token", "refresh_token", "role"} <= public_user.keys()
    claims = jwt.decode(public_user["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["role"] == "user"
    assert claims["token_type"] == "access"


def test_tc_auth_08_login_wrong_password_401(client, public_user):
    resp = client.post(
        "/api/v1/auth/login", json={"email": public_user["email"], "password": "wrong-pass"}
    )
    assert resp.status_code == 401


def test_tc_auth_09_login_unknown_email_401(client):
    resp = client.post("/api/v1/auth/login", json={"email": new_email(), "password": PASSWORD})
    assert resp.status_code == 401


def test_tc_auth_10_login_empty_body_422(client):
    assert client.post("/api/v1/auth/login", json={}).status_code == 422


def test_tc_auth_11_login_error_does_not_reveal_which_field_was_wrong(client, public_user):
    wrong_pw = client.post(
        "/api/v1/auth/login", json={"email": public_user["email"], "password": "nope"}
    )
    wrong_email = client.post("/api/v1/auth/login", json={"email": new_email(), "password": "x"})
    assert wrong_pw.json()["detail"] == wrong_email.json()["detail"]


# ---------- /me ----------


def test_tc_auth_12_me_with_valid_token(client, public_user):
    resp = client.get("/api/v1/auth/me", headers=bearer(public_user["access_token"]))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user_id"] and body["role"] == "PUBLIC"


def test_tc_auth_13_me_without_token_rejected(client):
    assert client.get("/api/v1/auth/me").status_code in (401, 403)


def test_tc_auth_14_me_with_garbage_token_401(client):
    assert client.get("/api/v1/auth/me", headers=bearer("not.a.jwt")).status_code == 401


def test_tc_auth_15_me_with_expired_token_401(client):
    expired = jwt.encode(
        {
            "sub": "USR-EXPIRED",
            "role": "user",
            "token_type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    assert client.get("/api/v1/auth/me", headers=bearer(expired)).status_code == 401


def test_tc_auth_16_me_rejects_refresh_token(client, public_user):
    resp = client.get("/api/v1/auth/me", headers=bearer(public_user["refresh_token"]))
    assert resp.status_code == 401


@pytest.mark.xfail(
    strict=True, reason="DEF-M1-002: /auth/me returns 'username' but the contract says 'name'"
)
def test_tc_auth_17_me_matches_contract_fields(client, public_user):
    body = client.get("/api/v1/auth/me", headers=bearer(public_user["access_token"])).json()
    assert {"user_id", "name", "role"} <= body.keys()


# ---------- Refresh ----------


def test_tc_auth_18_refresh_returns_new_access_token(client, public_user):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": public_user["refresh_token"]})
    assert resp.status_code == 200, resp.text
    new_token = resp.json()["access_token"]
    assert client.get("/api/v1/auth/me", headers=bearer(new_token)).status_code == 200


def test_tc_auth_19_refresh_rejects_access_token(client, public_user):
    resp = client.post("/api/v1/auth/refresh", json={"refresh_token": public_user["access_token"]})
    assert resp.status_code == 401


def test_tc_auth_20_refresh_rejects_garbage(client):
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": "x"}).status_code == 401


def test_tc_auth_21_password_is_not_stored_in_plain_text(client):
    from app.database import SessionLocal
    from app.models.user import User

    email = new_email()
    assert register(client, email).status_code == 201
    db = SessionLocal()
    try:
        stored = db.query(User).filter(User.email == email).one().password_hash
    finally:
        db.close()
    assert stored != PASSWORD and PASSWORD not in stored

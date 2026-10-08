from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from app.main import app
from app.routes.auth import create_access_token
from app.security import config
from app.security import auth as security_auth
from app.security import jwt as jwt_helpers


def test_jwt_helper_uses_centralized_secret():
    assert jwt_helpers.SECRET_KEY == config.SECRET_KEY
    assert jwt_helpers.ALGORITHM == config.ALGORITHM


def test_security_auth_dependency_decodes_valid_token():
    access_token = create_access_token({"sub": "qa-user", "username": "qa-user", "role": "user"})
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=access_token,
    )

    user = security_auth.get_current_user(credentials)

    assert user["user_id"] == "qa-user"
    assert user["role"] == "user"


def test_duplicate_registration_does_not_reset_password():
    email = "qa-register@gmail.com"
    with TestClient(app) as client:
        first = client.post(
            "/api/v1/auth/register",
            json={"name": "QA Register", "email": email, "password": "OriginalPass123!"},
        )
        assert first.status_code == 201

        duplicate = client.post(
            "/api/v1/auth/register",
            json={"name": "QA Register", "email": email, "password": "ReplacementPass123!"},
        )
        assert duplicate.status_code == 409

        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "OriginalPass123!"},
        )
        assert login.status_code == 200

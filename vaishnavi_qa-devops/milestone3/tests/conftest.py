"""Shared fixtures for the Milestone 3 QA suite.

python -m pytest QA/milestone3/tests            # unit + live (live skipped if stack is down)
python -m pytest QA/milestone3/tests -m "not live"
M3_BASE_URL=http://127.0.0.1:8000 python -m pytest QA/milestone3/tests -m live
"""

import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(
    os.getenv(
        "M3_BACKEND_DIR",
        os.getenv(
            "BACKEND_DIR",
            str(REPO_ROOT / "backend_updated" / "backend" / "Intern_AI AND ML"),
        ),
    )
)
BASE_URL = os.getenv("M3_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ANALYTICS_URL = os.getenv("M3_ANALYTICS_URL", "http://127.0.0.1:8001").rstrip("/")

# Alert producers (congestion watcher, anomaly detector) live at the backend root.
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "src"))
sys.path.insert(0, str(REPO_ROOT / "QA" / "milestone3"))

import qa_auth  # noqa: E402

qa_auth.load_dev_env()


def pytest_configure(config):
    config.addinivalue_line("markers", "live: needs the docker-compose.dev.yml stack running")
    config.addinivalue_line("markers", "analytics: needs the Analytics service on M3_ANALYTICS_URL")


def _service_up(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "live" in item.keywords and "analytics" not in item.keywords:
            if not _service_up(BASE_URL + "/health"):
                item.add_marker(pytest.mark.skip(reason=f"gateway not reachable at {BASE_URL}"))
        if "analytics" in item.keywords and not _service_up(ANALYTICS_URL + "/"):
            item.add_marker(
                pytest.mark.skip(reason=f"analytics service not reachable at {ANALYTICS_URL}")
            )


class Api:
    def __init__(self, base):
        self.base = base

    def request(self, method, path, body=None, token=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        for key, value in (headers or {}).items():
            req.add_header(key, value)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                status, raw = resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            status, raw = exc.code, exc.read()
        return status, (json.loads(raw) if raw else None)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, body, **kw):
        return self.request("POST", path, body, **kw)

    def patch(self, path, **kw):
        return self.request("PATCH", path, **kw)


@pytest.fixture(scope="session")
def api():
    return Api(BASE_URL)


@pytest.fixture(scope="session")
def user_token(api):
    """Access token for a fresh public user (registration forces role=user)."""
    run_id = uuid.uuid4().hex[:8]
    creds = {"email": f"qa.m3.{run_id}@gmail.com", "password": "QaPass#2026"}
    status, _ = api.post("/api/v1/auth/register", {"name": f"qa_m3_{run_id}", **creds})
    assert status == 201
    status, body = api.post("/api/v1/auth/login", creds)
    assert status == 200
    return body["access_token"]


@pytest.fixture
def unique_road():
    """A road id no other test uses, so assertions aren't polluted by existing alerts."""
    return f"QA-{uuid.uuid4().hex[:6].upper()}"


@pytest.fixture(scope="session")
def service_headers():
    """Internal producer key for POST /alerts (from .env.dev)."""
    return qa_auth.service_headers()


@pytest.fixture(scope="session")
def role_tokens():
    """JWTs for a fresh public user, operator and admin (operator/admin promoted in the DB)."""
    return {
        role: qa_auth.role_token(BASE_URL, role, "qa.m3") for role in ("user", "operator", "admin")
    }

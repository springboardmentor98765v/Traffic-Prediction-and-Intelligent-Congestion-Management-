import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.main import app

client = TestClient(app)


def test_rate_limit_headers_present():
    res = client.get("/api/v1/traffic/live")
    assert res.status_code == 200
    assert "x-ratelimit-limit" in res.headers
    assert "x-ratelimit-remaining" in res.headers
    assert "x-ratelimit-reset" in res.headers
    limit = int(res.headers["x-ratelimit-limit"])
    assert limit > 0


def test_rate_limit_exempt_docs():
    res = client.get("/docs")
    assert res.status_code == 200
    # Docs are exempt from rate limit headers
    assert "x-ratelimit-limit" not in res.headers

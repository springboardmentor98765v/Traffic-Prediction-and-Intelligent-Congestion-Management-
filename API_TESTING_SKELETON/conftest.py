import os
import pytest
import requests

BASE_URL = os.getenv("TRAFFICVISION_API_URL", "http://localhost:8000")


@pytest.fixture
def api_url():
    return BASE_URL.rstrip("/")


@pytest.fixture
def http_session():
    session = requests.Session()
    yield session
    session.close()

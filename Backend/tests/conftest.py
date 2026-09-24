import pytest
from app.middleware.rate_limit import _rate_limit_cache


@pytest.fixture(autouse=True)
def reset_rate_limit_cache():
    """Clear rate limiting cache between tests to prevent test client 429 throttling."""
    _rate_limit_cache.clear()
    yield
    _rate_limit_cache.clear()

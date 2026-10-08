import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import analytics_cache


def test_cache_round_trip():
    store = {}

    class FakeRedis:
        def get(self, key):
            return store.get(key)

        def setex(self, key, ttl, value):
            store[key] = value

    with patch("analytics_cache._client", return_value=FakeRedis()):
        analytics_cache.set_cached("trends", {"road_id": "R001"}, {"ok": True})
        result = analytics_cache.get_cached("trends", {"road_id": "R001"})

    assert result == {"ok": True}


def test_cache_failure_does_not_break_service():
    class BrokenRedis:
        def get(self, key):
            raise RuntimeError("redis unavailable")

        def setex(self, key, ttl, value):
            raise RuntimeError("redis unavailable")

    with patch("analytics_cache._client", return_value=BrokenRedis()):
        assert analytics_cache.get_cached("heatmap", {"hour": 18}) is None
        analytics_cache.set_cached("heatmap", {"hour": 18}, {"ok": True})

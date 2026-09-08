import json
import time
from typing import Optional, Any, Dict

_in_memory_cache: Dict[str, tuple[Any, float]] = {}

_redis_client = None
_redis_available: Optional[bool] = None


def _check_redis():
    global _redis_client, _redis_available
    if _redis_available is not None:
        return _redis_client if _redis_available else None
    try:
        import redis
        client = redis.Redis(
            host="localhost",
            port=6379,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2
        )
        client.ping()
        _redis_client = client
        _redis_available = True
    except Exception:
        _redis_client = None
        _redis_available = False
    return _redis_client


def set_cache(key: str, data: Any, expiry: int = 60) -> None:
    """Store data in Redis with fallback to in-memory cache."""
    client = _check_redis()
    if client:
        try:
            client.set(key, json.dumps(data), ex=expiry)
            return
        except Exception:
            pass
    _in_memory_cache[key] = (data, time.time() + expiry)


def get_cache(key: str) -> Optional[Any]:
    """Retrieve data from Redis or in-memory fallback."""
    client = _check_redis()
    if client:
        try:
            data = client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass

    if key in _in_memory_cache:
        val, exp = _in_memory_cache[key]
        if time.time() < exp:
            return val
        else:
            del _in_memory_cache[key]
    return None
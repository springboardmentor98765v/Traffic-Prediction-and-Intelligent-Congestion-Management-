"""
TrafficVision AI — Redis Caching Layer (Day 4)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    Wraps Redis get/set with JSON serialization and a short TTL
    (time-to-live), so frequently-hit endpoints like /traffic/live
    don't have to query PostgreSQL on every single request.

Why this matters:
    /traffic/live will get polled constantly by the frontend dashboard
    (e.g. every 3-5 seconds by every connected user). Without caching,
    that's a fresh database query for every single poll, from every
    single user. Caching for a few seconds means many requests in that
    window get served instantly from memory instead of hitting the DB.

Requirements:
    pip install redis
"""

import json
import redis

# ---------------------------------------------------------
# CONFIG — matches Intern 5's local Redis service (Docker: redis:6379)
# ---------------------------------------------------------
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True,  # so we get strings back, not bytes
    "socket_connect_timeout": 2,  # fail fast if Redis is unreachable, don't hang
    "socket_timeout": 2,          # fail fast on read/write too
}

DEFAULT_TTL_SECONDS = 5  # how long cached data stays valid before expiring

_client = None


def get_redis_client():
    """Lazily create a single shared Redis connection."""
    global _client
    if _client is None:
        _client = redis.Redis(**REDIS_CONFIG)
    return _client


def cache_get(key: str):
    """Return cached value (parsed from JSON) or None if not cached/expired."""
    try:
        client = get_redis_client()
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        # If Redis is down or unreachable, fail gracefully — just act like
        # a cache miss so the API still works (slower, but not broken).
        return None


def cache_set(key: str, value, ttl: int = DEFAULT_TTL_SECONDS):
    """Store value as JSON with an expiry (TTL) in seconds."""
    try:
        client = get_redis_client()
        client.setex(key, ttl, json.dumps(value, default=str))
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        # Same graceful fallback — caching is a performance boost,
        # not something that should crash the whole API if it's unavailable.
        pass


def cache_delete(key: str):
    """Manually clear a cache key (useful for testing)."""
    try:
        client = get_redis_client()
        client.delete(key)
    except redis.exceptions.ConnectionError:
        pass

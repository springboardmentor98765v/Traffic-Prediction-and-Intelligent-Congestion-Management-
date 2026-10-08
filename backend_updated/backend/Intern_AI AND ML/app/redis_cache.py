import json
import os
import redis

# Redis key used for the complete live traffic response
LIVE_TRAFFIC_KEY = "traffic:live"


def get_redis_client():
    """
    Create and return a Redis client.
    REDIS_URL (e.g. a managed rediss:// URL with password) wins over host/port.
    """

    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis.from_url(redis_url, decode_responses=True)

    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
    )


def cache_live_traffic(client, traffic_data, ttl_seconds=None):
    """
    Store live traffic data in Redis with an expiry time.
    """

    if ttl_seconds is None:
        ttl_seconds = int(os.getenv("REDIS_TTL_SECONDS", "30"))

    client.setex(LIVE_TRAFFIC_KEY, ttl_seconds, json.dumps(traffic_data))


def get_cached_live_traffic(client):
    """
    Get live traffic data from Redis.
    Returns None if the cache does not exist.
    """

    value = client.get(LIVE_TRAFFIC_KEY)

    if value is None:
        return None

    return json.loads(value)


def clear_live_traffic_cache(client):
    """
    Delete live traffic cache.
    """

    client.delete(LIVE_TRAFFIC_KEY)


# ---------------------------------------------------------
# Sensor-level cache functions
# ---------------------------------------------------------


def cache_latest_reading(client, reading: dict, ttl_seconds: int = 300):
    """
    Cache the latest reading for a specific sensor.
    """

    key = f"traffic:sensor:{reading['sensor_id']}"

    client.setex(key, ttl_seconds, json.dumps(reading))


def get_latest_reading(client, sensor_id: str):
    """
    Get the latest cached reading for a sensor.
    """

    value = client.get(f"traffic:sensor:{sensor_id}")

    return json.loads(value) if value else None

import redis
import json

# Connect to Redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


def set_cache(key, data, expiry=60):
    """Store data in Redis with an expiry time."""
    redis_client.setex(
        key,
        expiry,
        json.dumps(data)
    )


def get_cache(key):
    """Retrieve data from Redis."""
    data = redis_client.get(key)

    if data:
        return json.loads(data)

    return None
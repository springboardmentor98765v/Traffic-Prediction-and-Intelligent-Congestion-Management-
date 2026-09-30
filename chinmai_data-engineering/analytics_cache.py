import hashlib
import json
import os
import threading
import time
from queue import Queue, Empty

import redis


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

CACHE_TTL = int(
    os.getenv(
        "ANALYTICS_CACHE_TTL",
        "60"
    )
)

REDIS_OPERATION_TIMEOUT = float(
    os.getenv(
        "REDIS_OPERATION_TIMEOUT",
        "1.0"
    )
)

REDIS_COOLDOWN_SECONDS = int(
    os.getenv(
        "REDIS_COOLDOWN_SECONDS",
        "30"
    )
)

_redis_down_until = 0.0


def _client():
    return redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )


def _cache_key(prefix, values):
    raw = json.dumps(
        values,
        sort_keys=True,
        default=str
    )

    digest = hashlib.sha256(
        raw.encode()
    ).hexdigest()

    return f"analytics:{prefix}:{digest}"


def _redis_available():
    return time.monotonic() >= _redis_down_until


def _mark_redis_down():
    global _redis_down_until

    _redis_down_until = (
        time.monotonic()
        + REDIS_COOLDOWN_SECONDS
    )


def _mark_redis_up():
    global _redis_down_until

    _redis_down_until = 0.0


def _run_with_timeout(operation):
    result_queue = Queue(maxsize=1)

    def worker():
        try:
            result = operation()

            result_queue.put(
                (
                    True,
                    result
                )
            )

        except Exception as exc:
            result_queue.put(
                (
                    False,
                    exc
                )
            )

    thread = threading.Thread(
        target=worker,
        daemon=True
    )

    thread.start()

    try:
        success, result = result_queue.get(
            timeout=REDIS_OPERATION_TIMEOUT
        )

    except Empty:
        raise TimeoutError(
            "Redis operation timed out"
        )

    if not success:
        raise result

    return result


def get_cached(prefix, values):
    if not _redis_available():
        return None

    key = _cache_key(
        prefix,
        values
    )

    try:
        client = _client()

        cached = _run_with_timeout(
            lambda: client.get(key)
        )

        if cached is None:
            return None

        _mark_redis_up()

        return json.loads(cached)

    except Exception:
        _mark_redis_down()

        return None


def set_cached(
    prefix,
    values,
    data,
    ttl=CACHE_TTL
):
    if not _redis_available():
        return

    key = _cache_key(
        prefix,
        values
    )

    try:
        client = _client()

        _run_with_timeout(
            lambda: client.setex(
                key,
                ttl,
                json.dumps(
                    data,
                    default=str
                )
            )
        )

        _mark_redis_up()

    except Exception:
        _mark_redis_down()
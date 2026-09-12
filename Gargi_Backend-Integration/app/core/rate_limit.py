import time

from fastapi import HTTPException

_requests = {}

WINDOW_SECONDS = 60
MAX_REQUESTS = 60


def check_rate_limit(client_id: str):
    current_time = time.time()

    request_times = _requests.get(
        client_id,
        [],
    )

    request_times = [
        timestamp
        for timestamp in request_times
        if current_time - timestamp < WINDOW_SECONDS
    ]

    if len(request_times) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
        )

    request_times.append(current_time)

    _requests[client_id] = request_times

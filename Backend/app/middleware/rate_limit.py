import time
import os
from typing import Dict, Tuple, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# IP/User -> (timestamp_of_window_start, request_count)
_rate_limit_cache: Dict[str, Tuple[float, int]] = {}

WINDOW_SECONDS = 60
DEFAULT_LIMIT = 60
OPERATOR_LIMIT = 120
ADMIN_LIMIT = 300


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled:
            return await call_next(request)

        # Skip rate-limiting for docs and health
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/openapi") or path.startswith("/redoc") or path == "/health" or path == "/":
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"

        # Check authorization header for role-based tier
        auth_header = request.headers.get("Authorization", "")
        limit = DEFAULT_LIMIT
        identifier = client_ip

        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                from app.services.jwt_service import decode_token
                payload = decode_token(token)
                if payload:
                    user_id = payload.get("sub")
                    identifier = f"user:{user_id}"
                    # Check role in payload if present
                    role = payload.get("role", "public").lower()
                    if role == "admin":
                        limit = ADMIN_LIMIT
                    elif role == "operator":
                        limit = OPERATOR_LIMIT
            except Exception:
                pass

        now = time.time()
        window_start, count = _rate_limit_cache.get(identifier, (now, 0))

        if now - window_start >= WINDOW_SECONDS:
            # New window
            window_start = now
            count = 0

        count += 1
        _rate_limit_cache[identifier] = (window_start, count)

        remaining = max(0, limit - count)
        reset_time = int(WINDOW_SECONDS - (now - window_start))

        if count > limit:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Maximum {limit} requests per minute."},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time)
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        return response

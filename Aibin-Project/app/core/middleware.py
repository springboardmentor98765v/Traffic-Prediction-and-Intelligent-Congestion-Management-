"""
Production Middlewares for TrafficVision AI API Gateway:
- Request ID generation & propagation (X-Request-ID)
- Security Headers (HSTS, nosniff, frame-options, referrer policy)
- Structured Request Logging with timing
- IP-based Rate Limiting (429 Too Many Requests with Retry-After)
- Payload Size Limiting (413 Payload Too Large)
"""

import time
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from ..config import settings
from .rate_limiter import rate_limiter

logger = logging.getLogger("gateway.access")
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


def get_client_ip(request: Request) -> str:
    """Extracts client IP, respecting proxy headers if TRUST_PROXIES is enabled."""
    if settings.TRUST_PROXIES:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # First IP in comma-separated list is the client IP
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


class GatewayProductionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Force HTTPS redirect if configured and behind proxy
        if settings.FORCE_HTTPS:
            proto = request.headers.get("x-forwarded-proto", request.url.scheme)
            if proto == "http":
                secure_url = request.url.replace(scheme="https")
                return RedirectResponse(url=str(secure_url), status_code=301)

        # 2. Body size check (413 Payload Too Large)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.MAX_REQUEST_BODY_SIZE_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request payload exceeds maximum allowed size (10 MB)."}
                    )
            except ValueError:
                pass

        # 3. Extract or generate Request ID
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        # 4. Rate Limiting Check (Skip for internal health probes)
        path = request.url.path
        if path not in ["/health", "/ready", "/docs", "/openapi.json"]:
            client_ip = get_client_ip(request)
            allowed, retry_after = await rate_limiter.check_rate_limit(client_ip, path)
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    headers={
                        "Retry-After": str(retry_after),
                        "X-Request-ID": request_id
                    },
                    content={
                        "detail": f"Too many requests. Rate limit exceeded. Please retry after {retry_after} seconds."
                    }
                )

        # 5. Process Request & Measure Duration
        start_time = time.time()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                f"[GATEWAY ERROR] request_id={request_id} client={get_client_ip(request)} "
                f"method={request.method} path={path} duration={duration_ms}ms error={str(exc)}"
            )
            return JSONResponse(
                status_code=500,
                headers={"X-Request-ID": request_id},
                content={"detail": "Internal server error occurred in Gateway."}
            )

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Apply Security Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Apply HSTS in production
        if settings.APP_ENV.lower() == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 7. Structured Access Logging
        logger.info(
            f"[ACCESS] request_id={request_id} client={get_client_ip(request)} "
            f"method={request.method} path={path} status={response.status_code} duration={duration_ms}ms"
        )

        return response

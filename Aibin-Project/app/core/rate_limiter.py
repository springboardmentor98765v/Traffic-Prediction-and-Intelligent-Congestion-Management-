"""
Production Rate Limiter for TrafficVision AI API Gateway.
Provides in-memory sliding-window rate limiting with IP-based bucket isolation.
Supports configurable global limits and stricter limits on sensitive authentication routes.
"""

import time
import asyncio
from typing import Dict, List, Tuple
from ..config import settings


class InMemoryRateLimiter:
    def __init__(self):
        # Maps ip -> list of timestamps (epoch seconds)
        self._global_buckets: Dict[str, List[float]] = {}
        self._auth_buckets: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()

    async def check_rate_limit(self, client_ip: str, path: str) -> Tuple[bool, int]:
        """
        Evaluates whether a request from client_ip is allowed under configured policies.
        Returns:
            (allowed: bool, retry_after: int)
        """
        now = time.time()
        window_seconds = 60.0

        async with self._lock:
            # Periodic cleanup every 5 minutes to prevent memory leak
            if now - self._last_cleanup > 300:
                self._cleanup_stale(now)
                self._last_cleanup = now

            # Check if this is a sensitive auth route (login/register)
            is_auth_route = path.rstrip("/").endswith("/api/v1/auth/login") or path.rstrip("/").endswith("/api/v1/auth/register")
            
            if is_auth_route:
                limit = settings.RATE_LIMIT_AUTH_PER_MIN
                bucket = self._auth_buckets.setdefault(client_ip, [])
            else:
                limit = settings.RATE_LIMIT_GLOBAL_PER_MIN
                bucket = self._global_buckets.setdefault(client_ip, [])

            # Purge timestamps older than the sliding window
            cutoff = now - window_seconds
            bucket[:] = [ts for ts in bucket if ts > cutoff]

            if len(bucket) >= limit:
                # Exceeded rate limit! Calculate time until the oldest request expires
                oldest_ts = bucket[0]
                retry_after = max(1, int(window_seconds - (now - oldest_ts)))
                return False, retry_after

            # Within limit: record this request timestamp
            bucket.append(now)
            return True, 0

    def _cleanup_stale(self, now: float):
        cutoff = now - 60.0
        for ip in list(self._global_buckets.keys()):
            self._global_buckets[ip] = [ts for ts in self._global_buckets[ip] if ts > cutoff]
            if not self._global_buckets[ip]:
                del self._global_buckets[ip]

        for ip in list(self._auth_buckets.keys()):
            self._auth_buckets[ip] = [ts for ts in self._auth_buckets[ip] if ts > cutoff]
            if not self._auth_buckets[ip]:
                del self._auth_buckets[ip]


rate_limiter = InMemoryRateLimiter()

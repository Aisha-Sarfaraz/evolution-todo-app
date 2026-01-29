"""Rate limiting middleware.

T083: [US3] Implement rate limiting middleware
100 requests/minute per user using in-memory counter.
Returns 429 with Retry-After header when limit exceeded.
"""

import os
import time
from collections import defaultdict
from typing import Callable, Optional
from dataclasses import dataclass
from threading import Lock

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Check if running in test environment
IS_TEST_ENVIRONMENT = os.getenv("ENVIRONMENT", "").lower() == "test"


@dataclass
class RateLimitEntry:
    """Rate limit entry for a user/IP."""

    count: int = 0
    window_start: float = 0.0


class RateLimitStore:
    """Thread-safe in-memory rate limit store."""

    def __init__(self, window_seconds: int = 60, max_requests: int = 100):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self._store: dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self._lock = Lock()

    def check_and_increment(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed and increment counter.

        Returns:
            tuple of (is_allowed, seconds_until_reset)
        """
        current_time = time.time()

        with self._lock:
            entry = self._store[key]

            # Check if window has expired
            if current_time - entry.window_start >= self.window_seconds:
                # Reset window
                entry.count = 1
                entry.window_start = current_time
                return (True, 0)

            # Check if under limit
            if entry.count < self.max_requests:
                entry.count += 1
                return (True, 0)

            # Rate limited
            seconds_remaining = int(self.window_seconds - (current_time - entry.window_start))
            return (False, max(1, seconds_remaining))

    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        with self._lock:
            entry = self._store[key]
            current_time = time.time()

            if current_time - entry.window_start >= self.window_seconds:
                return self.max_requests

            return max(0, self.max_requests - entry.count)

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        with self._lock:
            if key in self._store:
                del self._store[key]


# Global rate limit store instance
_rate_limit_store: Optional[RateLimitStore] = None


def get_rate_limit_store(
    window_seconds: int = 60,
    max_requests: int = 100,
) -> RateLimitStore:
    """Get or create the rate limit store singleton."""
    global _rate_limit_store
    if _rate_limit_store is None:
        _rate_limit_store = RateLimitStore(
            window_seconds=window_seconds,
            max_requests=max_requests,
        )
    return _rate_limit_store


def reset_rate_limit_store() -> None:
    """Reset the global rate limit store. Useful for testing."""
    global _rate_limit_store
    if _rate_limit_store is not None:
        _rate_limit_store._store.clear()


def extract_user_key(request: Request) -> str:
    """
    Extract rate limit key from request.

    Priority:
    1. User ID from JWT token (if authenticated)
    2. Client IP address (if unauthenticated)
    """
    # Try to get user_id from request state (set by JWT validation)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    # Fall back to IP address
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Use first IP in chain (original client)
        client_ip = forwarded_for.split(",")[0].strip()

    return f"ip:{client_ip}"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Limits requests per user/IP to prevent abuse.
    Default: 100 requests per minute.
    """

    def __init__(
        self,
        app,
        window_seconds: int = 60,
        max_requests: int = 100,
        exclude_paths: Optional[list[str]] = None,
    ):
        super().__init__(app)
        self.store = get_rate_limit_store(window_seconds, max_requests)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and apply rate limiting."""
        # Skip rate limiting in test environment
        if IS_TEST_ENVIRONMENT:
            return await call_next(request)

        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Extract rate limit key
        key = extract_user_key(request)

        # Check rate limit
        is_allowed, retry_after = self.store.check_and_increment(key)

        if not is_allowed:
            # Return 429 Too Many Requests
            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMITED",
                    "detail": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.store.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = self.store.get_remaining(key)
        response.headers["X-RateLimit-Limit"] = str(self.store.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response


def create_rate_limit_dependency(
    window_seconds: int = 60,
    max_requests: int = 100,
):
    """
    Create a FastAPI dependency for rate limiting specific endpoints.

    Usage:
        @app.get("/api/resource", dependencies=[Depends(rate_limit(10, 60))])
        async def get_resource():
            ...
    """
    from fastapi import HTTPException

    store = get_rate_limit_store(window_seconds, max_requests)

    async def rate_limit_check(request: Request):
        key = extract_user_key(request)
        is_allowed, retry_after = store.check_and_increment(key)

        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

    return rate_limit_check


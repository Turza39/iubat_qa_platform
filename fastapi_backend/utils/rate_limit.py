"""
Rate limiting middleware using Redis.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import settings
from utils.redis_cache import check_rate_limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based rate limiting middleware.
    
    Limits requests per user (if authenticated) or IP address.
    Works across multiple replicas since it uses Redis.
    """

    def __init__(
        self,
        app: ASGIApp,
        requests: int = None,
        window_seconds: int = None,
    ):
        super().__init__(app)
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.requests = requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting if disabled
        if not self.enabled:
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc"]:
            return await call_next(request)

        # Get identifier (user_id if authenticated, otherwise client IP)
        identifier = self._get_identifier(request)

        # Check rate limit
        is_allowed, remaining = await check_rate_limit(
            identifier=identifier,
            limit=self.requests,
            window_seconds=self.window_seconds
        )

        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(self.window_seconds)

        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Max {self.requests} requests per {self.window_seconds} seconds.",
                    "retry_after": self.window_seconds,
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.window_seconds),
                }
            )

        return response

    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Uses user_id if authenticated, otherwise uses client IP.
        """
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Fall back to client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # If behind proxy, check X-Forwarded-For
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
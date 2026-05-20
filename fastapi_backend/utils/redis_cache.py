import json
import ssl
from typing import Any, Optional

import redis
import redis.asyncio as aioredis

from config import settings

_async_client: Optional[aioredis.Redis] = None
_sync_client: Optional[redis.Redis] = None


def get_redis_url() -> str:
    return settings.REDIS_URL


def _is_ssl(url: str) -> bool:
    return url.startswith("rediss://") or settings.REDIS_SSL


def _create_ssl_context() -> ssl.SSLContext:
    """Create SSL context for Upstash (no cert verification)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


# =========================
# ASYNC CLIENT
# =========================
async def get_async_redis() -> aioredis.Redis:
    global _async_client

    # Always create fresh connection to avoid stale state
    url = get_redis_url()
    
    # Remove query params from URL
    if "?" in url:
        url = url.split("?")[0]

    common_args = dict(
        decode_responses=True,
        health_check_interval=30,
    )

    if _is_ssl(url):
        _async_client = aioredis.from_url(
            url,
            ssl=True,
            ssl_context=_create_ssl_context(),
            **common_args,
        )
    else:
        _async_client = aioredis.from_url(url, **common_args)

    return _async_client


# =========================
# SYNC CLIENT
# =========================
def get_sync_redis() -> redis.Redis:
    global _sync_client

    url = get_redis_url()
    
    # Remove query params from URL
    if "?" in url:
        url = url.split("?")[0]

    common_args = dict(
        decode_responses=True,
        health_check_interval=30,
    )

    if _is_ssl(url):
        _sync_client = redis.from_url(
            url,
            ssl=True,
            ssl_context=_create_ssl_context(),
            **common_args,
        )
    else:
        _sync_client = redis.from_url(url, **common_args)

    return _sync_client


# =========================
# CACHE HELPERS
# =========================
async def get_cached_json(key: str) -> Optional[Any]:
    try:
        redis_client = await get_async_redis()
        value = await redis_client.get(key)

        if not value:
            return None

        return json.loads(value)

    except Exception:
        # Redis failure should never crash API
        return None


async def set_cached_json(key: str, value: Any, ttl: int) -> None:
    try:
        redis_client = await get_async_redis()
        await redis_client.set(
            key,
            json.dumps(value, default=str),
            ex=ttl
        )
    except Exception:
        pass


async def delete_keys(*keys: str) -> int:
    if not keys:
        return 0

    try:
        redis_client = await get_async_redis()
        return await redis_client.delete(*keys)
    except Exception:
        return 0


# =========================
# PATTERN DELETE (OPTIMIZED)
# =========================
async def delete_pattern(pattern: str) -> int:
    try:
        redis_client = await get_async_redis()
        deleted = 0

        async for key in redis_client.scan_iter(match=pattern):
            deleted += await redis_client.delete(key)

        return deleted
    except Exception:
        return 0


def delete_pattern_sync(pattern: str) -> int:
    try:
        redis_client = get_sync_redis()

        pipe = redis_client.pipeline()
        count = 0

        for key in redis_client.scan_iter(match=pattern):
            pipe.delete(key)
            count += 1

        pipe.execute()
        return count

    except Exception:
        return 0


# =========================
# RATE LIMIT (SAFE + ATOMIC)
# =========================
async def check_rate_limit(identifier: str, limit: int, window_seconds: int):
    try:
        redis_client = await get_async_redis()
        key = f"rate_limit:{identifier}"

        current = await redis_client.incr(key)

        if current == 1:
            await redis_client.expire(key, window_seconds)

        return current <= limit, max(0, limit - current)

    except Exception:
        # NEVER block API if Redis is down
        return True, limit


async def reset_rate_limit(identifier: str) -> int:
    try:
        redis_client = await get_async_redis()
        return await redis_client.delete(f"rate_limit:{identifier}")
    except Exception:
        return 0
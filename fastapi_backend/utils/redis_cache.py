import json
from typing import Any, Optional

import redis
import redis.asyncio as aioredis

from config import settings

_async_client: Optional[aioredis.Redis] = None
_sync_client: Optional[redis.Redis] = None


def get_redis_url() -> str:
    return settings.REDIS_URL


async def get_async_redis() -> aioredis.Redis:
    global _async_client
    if _async_client is None:
        _async_client = aioredis.from_url(
            get_redis_url(),
            decode_responses=True,
            health_check_interval=30,
        )
    return _async_client


def get_sync_redis() -> redis.Redis:
    global _sync_client
    if _sync_client is None:
        _sync_client = redis.from_url(
            get_redis_url(),
            decode_responses=True,
            health_check_interval=30,
        )
    return _sync_client


async def get_cached_json(key: str) -> Optional[Any]:
    redis_client = await get_async_redis()
    raw_value = await redis_client.get(key)
    if raw_value is None:
        return None
    try:
        return json.loads(raw_value)
    except json.JSONDecodeError:
        return None


async def set_cached_json(key: str, value: Any, ttl: int) -> None:
    redis_client = await get_async_redis()
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)


async def delete_keys(*keys: str) -> int:
    if not keys:
        return 0
    redis_client = await get_async_redis()
    return await redis_client.delete(*keys)


async def delete_pattern(pattern: str) -> int:
    redis_client = await get_async_redis()
    deleted = 0
    async for key in redis_client.scan_iter(match=pattern):
        deleted += await redis_client.delete(key)
    return deleted


def delete_pattern_sync(pattern: str) -> int:
    redis_client = get_sync_redis()
    deleted = 0
    for key in redis_client.scan_iter(match=pattern):
        deleted += redis_client.delete(key)
    return deleted

"""Redis risk-velocity cache with graceful fallback to in-memory dict."""
import os
import json
from typing import Optional

_redis = None
_mem: dict = {}


async def connect() -> None:
    global _redis
    try:
        import redis.asyncio as aioredis
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        _redis = await aioredis.from_url(f"redis://{host}:{port}", socket_connect_timeout=2)
        await _redis.ping()
        print("[Redis] Connected")
    except Exception as e:
        print(f"[Redis] Unavailable — using in-memory cache: {e}")
        _redis = None


async def disconnect() -> None:
    if _redis:
        await _redis.aclose()


async def set_risk(account: str, data: dict, ttl: int = 3600) -> None:
    key = f"risk:{account}"
    if _redis:
        await _redis.setex(key, ttl, json.dumps(data))
    else:
        _mem[key] = data


async def get_risk(account: str) -> Optional[dict]:
    key = f"risk:{account}"
    if _redis:
        raw = await _redis.get(key)
        return json.loads(raw) if raw else None
    return _mem.get(key)

"""MongoDB async client using Motor. Falls back gracefully when Mongo is unavailable."""
import os
from typing import Optional

_client = None
_db = None


async def connect() -> None:
    global _client, _db
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB", "finguard")
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
        await _client.server_info()
        _db = _client[db_name]
        await _ensure_indexes()
        print(f"[MongoDB] Connected to {db_name}")
    except Exception as e:
        print(f"[MongoDB] Unavailable — running without persistence: {e}")
        _client = None
        _db = None


async def disconnect() -> None:
    global _client
    if _client:
        _client.close()


def get_db():
    return _db


async def _ensure_indexes() -> None:
    if _db is None:
        return
    await _db["transactions"].create_index("tx_id", unique=True)
    await _db["transactions"].create_index("from_account")
    await _db["transactions"].create_index("timestamp")
    await _db["alerts"].create_index("alert_id", unique=True)
    await _db["alerts"].create_index("risk_score")
    await _db["alerts"].create_index("status")

"""GET /api/alerts — paginated alert list from MongoDB or in-memory fallback."""
from fastapi import APIRouter, Query
from datetime import datetime

router = APIRouter()

_mem_alerts: list[dict] = []


def push_alert(alert: dict) -> None:
    _mem_alerts.insert(0, alert)
    if len(_mem_alerts) > 500:
        _mem_alerts.pop()


@router.get("/alerts")
async def list_alerts(
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0),
    min_score: float = Query(0.0, ge=0),
    status: str = Query(""),
):
    from backend.db.mongo import get_db
    db = get_db()
    if db is not None:
        filt: dict = {}
        if min_score > 0:
            filt["risk_score"] = {"$gte": min_score}
        if status:
            filt["status"] = status
        cursor = db["alerts"].find(filt, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        return {"alerts": await cursor.to_list(length=limit)}
    # fallback
    filtered = [a for a in _mem_alerts
                if a.get("risk_score", 0) >= min_score
                and (not status or a.get("status") == status)]
    return {"alerts": filtered[skip: skip + limit], "total": len(filtered)}


@router.get("/alerts/stats")
async def alert_stats():
    from backend.db.mongo import get_db
    db = get_db()
    if db is not None:
        pipeline = [{"$group": {"_id": "$risk_level", "count": {"$sum": 1},
                                "total_value": {"$sum": "$amount"}}}]
        result = await db["alerts"].aggregate(pipeline).to_list(length=10)
        return {"stats": result}
    counts = {}
    for a in _mem_alerts:
        counts[a.get("risk_level", "?")] = counts.get(a.get("risk_level", "?"), 0) + 1
    return {"stats": [{"_id": k, "count": v} for k, v in counts.items()]}

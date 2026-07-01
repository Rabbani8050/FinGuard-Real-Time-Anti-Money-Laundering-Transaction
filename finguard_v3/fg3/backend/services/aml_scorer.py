"""Service wrapper that calls the AI inference engine and persists results."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from ai_engine.inference import get_engine
from backend.db.mongo import get_db
from backend.db.schemas import tx_doc, alert_doc
from backend.db.cache import set_risk


async def score_transaction(tx: dict) -> dict:
    engine = get_engine()
    result = engine.score(tx)

    db = get_db()
    if db is not None:
        try:
            await db["transactions"].insert_one(tx_doc(tx, result))
            if result["flagged"]:
                await db["alerts"].insert_one(alert_doc(tx, result))
        except Exception:
            pass

    await set_risk(tx.get("from_account", ""), {
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "last_tx": str(tx.get("tx_id")),
    })

    return result

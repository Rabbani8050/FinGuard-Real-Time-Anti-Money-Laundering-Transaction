"""MongoDB document helpers (no Beanie ODM to keep zero-infra startup)."""
from datetime import datetime


def tx_doc(tx: dict, score_result: dict) -> dict:
    return {
        "tx_id":        tx.get("tx_id"),
        "from_account": tx.get("from_account"),
        "to_account":   tx.get("to_account"),
        "amount":       tx.get("amount"),
        "currency":     tx.get("currency", "USD"),
        "risk_score":   score_result.get("risk_score"),
        "risk_level":   score_result.get("risk_level"),
        "flagged":      score_result.get("flagged"),
        "pattern_tags": score_result.get("pattern_tags"),
        "model_used":   score_result.get("model_used"),
        "created_at":   datetime.utcnow(),
    }


def alert_doc(tx: dict, score_result: dict) -> dict:
    import uuid
    return {
        "alert_id":       f"AML-{str(uuid.uuid4())[:4].upper()}",
        "tx_id":          tx.get("tx_id"),
        "from_account":   tx.get("from_account"),
        "to_account":     tx.get("to_account"),
        "amount":         tx.get("amount"),
        "risk_score":     score_result.get("risk_score"),
        "risk_level":     score_result.get("risk_level"),
        "pattern_tags":   score_result.get("pattern_tags"),
        "model_used":     score_result.get("model_used"),
        "status":         "OPEN",
        "created_at":     datetime.utcnow(),
    }

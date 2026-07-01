"""POST /api/tx — ingest and score a single transaction."""
from fastapi import APIRouter
from datetime import datetime
from backend.models.transaction import Transaction, TransactionResponse
from backend.services.aml_scorer import score_transaction
from backend.services.graph_builder import add_transaction

router = APIRouter()


@router.post("/tx", response_model=TransactionResponse)
async def ingest_transaction(tx: Transaction):
    tx_dict = tx.model_dump()
    tx_dict["timestamp"] = tx_dict.get("timestamp") or datetime.utcnow()
    result = await score_transaction(tx_dict)
    add_transaction(tx.from_account, tx.to_account, tx.amount, result["risk_level"])
    return TransactionResponse(
        tx_id=result["tx_id"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        flagged=result["flagged"],
        pattern_tags=result["pattern_tags"],
        model_used=result["model_used"],
        latency_ms=result["latency_ms"],
        timestamp=result["timestamp"],
    )

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Transaction(BaseModel):
    tx_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_account: str
    to_account: str
    amount: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    country_origin: Optional[str] = None
    country_dest: Optional[str] = None
    tx_type: str = "wire"
    reference: Optional[str] = None


class TransactionResponse(BaseModel):
    tx_id: str
    risk_score: float
    risk_level: str
    flagged: bool
    pattern_tags: list[str]
    model_used: str
    latency_ms: float
    timestamp: datetime

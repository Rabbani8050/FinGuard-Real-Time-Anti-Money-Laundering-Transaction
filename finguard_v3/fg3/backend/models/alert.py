from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"AML-{str(uuid.uuid4())[:4].upper()}")
    tx_id: str
    from_account: str
    to_account: str
    amount: float
    risk_score: float
    risk_level: str
    pattern_type: str
    pattern_tags: list[str]
    linked_accounts: list[str] = []
    model_used: str
    status: str = "OPEN"   # OPEN | REVIEW | FROZEN | CLEARED
    created_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

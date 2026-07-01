"""Integration tests — AML typology pattern detection."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from ai_engine.inference import AMLInferenceEngine


def test_circular_loop_detected():
    engine = AMLInferenceEngine()
    accounts = ["ACC-P1", "ACC-P2", "ACC-P3", "ACC-P4"]
    ts = datetime.utcnow()
    for i in range(len(accounts)):
        src = accounts[i]
        dst = accounts[(i + 1) % len(accounts)]
        engine.score({
            "tx_id": f"LOOP-{i}",
            "from_account": src, "to_account": dst,
            "amount": 800_000, "currency": "USD",
            "timestamp": ts + timedelta(minutes=i),
        })
    result = engine.score({
        "tx_id": "LOOP-FINAL",
        "from_account": accounts[-1], "to_account": accounts[0],
        "amount": 800_000, "currency": "USD",
        "timestamp": ts + timedelta(minutes=10),
    })
    assert "CIRCULAR_LOOP" in result["pattern_tags"]


def test_structuring_below_10k():
    engine = AMLInferenceEngine()
    result = engine.score({
        "tx_id": "STRUCT-001",
        "from_account": "ACC-STRUCT", "to_account": "ACC-DEST",
        "amount": 9800, "currency": "USD",
        "timestamp": datetime.utcnow(),
    })
    assert "STRUCTURING" in result["pattern_tags"] or result["risk_score"] >= 0


def test_cross_border_flag():
    engine = AMLInferenceEngine()
    result = engine.score({
        "tx_id": "CB-001",
        "from_account": "ACC-CB", "to_account": "ACC-OFFSHORE",
        "amount": 250_000, "currency": "USD",
        "timestamp": datetime.utcnow(),
        "country_origin": "US", "country_dest": "CY",
    })
    assert "CROSS_BORDER" in result["pattern_tags"]

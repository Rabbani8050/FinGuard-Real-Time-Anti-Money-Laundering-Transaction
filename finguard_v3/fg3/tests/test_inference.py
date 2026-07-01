"""Unit tests for the AI inference engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime


def make_tx(**kwargs):
    base = {
        "tx_id": "TEST-001",
        "from_account": "ACC-TEST",
        "to_account": "ACC-DEST",
        "amount": 50000.0,
        "currency": "USD",
        "timestamp": datetime.utcnow(),
        "country_origin": "US",
        "country_dest": "DE",
    }
    base.update(kwargs)
    return base


def test_engine_returns_expected_keys():
    from ai_engine.inference import AMLInferenceEngine
    engine = AMLInferenceEngine()
    result = engine.score(make_tx())
    assert "risk_score" in result
    assert "risk_level" in result
    assert "flagged" in result
    assert "pattern_tags" in result
    assert "latency_ms" in result


def test_risk_score_bounds():
    from ai_engine.inference import AMLInferenceEngine
    engine = AMLInferenceEngine()
    result = engine.score(make_tx())
    assert 0 <= result["risk_score"] <= 100


def test_large_amount_tag():
    from ai_engine.inference import AMLInferenceEngine
    engine = AMLInferenceEngine()
    result = engine.score(make_tx(amount=1_000_000))
    assert "LARGE_AMOUNT" in result["pattern_tags"]


def test_risk_level_values():
    from ai_engine.models.ensemble import EnsembleScorer
    e = EnsembleScorer()
    assert e.risk_level(0.95) == "CRITICAL"
    assert e.risk_level(0.80) == "HIGH"
    assert e.risk_level(0.60) == "MEDIUM"
    assert e.risk_level(0.40) == "LOW"
    assert e.risk_level(0.10) == "CLEAN"


def test_velocity_features_shape():
    from ai_engine.features.velocity_matrix import VelocityMatrix
    vm = VelocityMatrix()
    import numpy as np
    feats = vm.features("ACC-NEW")
    assert feats.shape == (5,)
    vm.update("ACC-A", 1000.0, datetime.utcnow())
    feats = vm.features("ACC-A")
    assert feats.shape == (5,)
    assert feats[0] == 1   # tx count


def test_graph_cycle_detection():
    from ai_engine.features.graph_embeddings import GraphEmbedder
    g = GraphEmbedder()
    g.add_edge("A", "B", 100)
    g.add_edge("B", "C", 100)
    g.add_edge("C", "A", 100)   # cycle
    assert g.has_cycle("A")


def test_graph_no_false_cycle():
    from ai_engine.features.graph_embeddings import GraphEmbedder
    g = GraphEmbedder()
    g.add_edge("X", "Y", 100)
    g.add_edge("Y", "Z", 100)
    assert not g.has_cycle("X")

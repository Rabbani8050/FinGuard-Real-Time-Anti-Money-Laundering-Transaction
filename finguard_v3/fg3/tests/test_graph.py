"""Unit tests for the backend graph builder service."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib


def fresh_builder():
    import backend.services.graph_builder as gb
    importlib.reload(gb)
    return gb


def test_add_and_retrieve():
    gb = fresh_builder()
    gb.add_transaction("ACC-1", "ACC-2", 5000, "LOW")
    payload = gb.get_graph_payload()
    ids = [n["id"] for n in payload["nodes"]]
    assert "ACC-1" in ids
    assert "ACC-2" in ids


def test_edge_risk_escalation():
    gb = fresh_builder()
    gb.add_transaction("ACC-A", "ACC-B", 1000, "LOW")
    gb.add_transaction("ACC-A", "ACC-B", 2000, "CRITICAL")
    payload = gb.get_graph_payload()
    edge = next(e for e in payload["edges"] if e["source"] == "ACC-A")
    assert edge["risk"] == "CRITICAL"


def test_payload_structure():
    gb = fresh_builder()
    payload = gb.get_graph_payload()
    assert "nodes" in payload
    assert "edges" in payload
    assert "cycles" in payload

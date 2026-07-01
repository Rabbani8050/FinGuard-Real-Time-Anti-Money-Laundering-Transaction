"""Build and query the account linkage graph for the /graph API."""
import networkx as nx
from collections import defaultdict

_G = nx.DiGraph()
_edge_meta: dict = {}


def add_transaction(src: str, dst: str, amount: float, risk_level: str) -> None:
    key = (src, dst)
    if _G.has_edge(src, dst):
        _G[src][dst]["weight"] += amount
        _G[src][dst]["count"]  += 1
        _G[src][dst]["risk"]    = risk_level if risk_level in ("CRITICAL", "HIGH") else _G[src][dst]["risk"]
    else:
        _G.add_edge(src, dst, weight=amount, count=1, risk=risk_level)


def get_graph_payload() -> dict:
    nodes = []
    for n in _G.nodes():
        in_w  = sum(d.get("weight", 0) for _, _, d in _G.in_edges(n, data=True))
        out_w = sum(d.get("weight", 0) for _, _, d in _G.out_edges(n, data=True))
        risk  = "high" if any(d.get("risk") in ("CRITICAL", "HIGH")
                               for _, _, d in _G.in_edges(n, data=True)) else "clean"
        nodes.append({"id": n, "in_volume": in_w, "out_volume": out_w, "risk": risk})

    edges = []
    for s, t, d in _G.edges(data=True):
        edges.append({"source": s, "target": t,
                      "weight": d.get("weight", 0),
                      "count":  d.get("count", 1),
                      "risk":   d.get("risk", "clean")})
    cycles = []
    try:
        cycles = [list(c) for c in nx.simple_cycles(_G)]
    except Exception:
        pass

    return {"nodes": nodes, "edges": edges, "cycles": cycles}

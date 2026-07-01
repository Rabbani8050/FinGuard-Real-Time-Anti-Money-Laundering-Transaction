"""Lightweight structural graph feature extraction using NetworkX."""
import numpy as np
import networkx as nx


class GraphEmbedder:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_edge(self, src: str, dst: str, amount: float) -> None:
        if self.G.has_edge(src, dst):
            self.G[src][dst]["weight"] += amount
            self.G[src][dst]["count"] += 1
        else:
            self.G.add_edge(src, dst, weight=amount, count=1)

    def node_features(self, node: str) -> np.ndarray:
        if node not in self.G:
            return np.zeros(5, dtype=np.float32)
        in_deg  = self.G.in_degree(node)
        out_deg = self.G.out_degree(node)
        in_w    = sum(d.get("weight", 0) for _, _, d in self.G.in_edges(node, data=True))
        out_w   = sum(d.get("weight", 0) for _, _, d in self.G.out_edges(node, data=True))
        try:
            pr = nx.pagerank(self.G, max_iter=50).get(node, 0.0)
        except Exception:
            pr = 0.0
        return np.array([in_deg, out_deg, in_w, out_w, pr], dtype=np.float32)

    def has_cycle(self, node: str) -> bool:
        try:
            return any(node in c for c in nx.simple_cycles(self.G))
        except Exception:
            return False

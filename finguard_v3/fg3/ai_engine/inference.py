"""Real-time scoring entrypoint."""
import time
import numpy as np
from datetime import datetime
from .models.ensemble import EnsembleScorer
from .features.velocity_matrix import VelocityMatrix
from .features.graph_embeddings import GraphEmbedder
from .features.behavioral_vectors import BehavioralVectors

class AMLInferenceEngine:
    def __init__(self):
        self.ensemble   = EnsembleScorer()
        self.velocity   = VelocityMatrix()
        self.graph      = GraphEmbedder()
        self.behavioral = BehavioralVectors()

    def _build_feature_vector(self, tx: dict) -> np.ndarray:
        src     = tx["from_account"]
        dst     = tx["to_account"]
        amt     = float(tx["amount"])
        ts      = tx.get("timestamp", datetime.utcnow())
        country = tx.get("country_origin", "US")
        self.velocity.update(src, amt, ts)
        self.graph.add_edge(src, dst, amt)
        self.behavioral.record(src, amt, ts, country)
        v_feat = self.velocity.features(src)
        g_feat = self.graph.node_features(src)
        return np.concatenate([v_feat, g_feat]).reshape(1, -1)

    def score(self, tx: dict) -> dict:
        t0     = time.perf_counter()
        X      = self._build_feature_vector(tx)
        result = self.ensemble.score(X, tx=tx)
        combined = float(result["combined"][0])
        level    = self.ensemble.risk_level(combined)
        tags     = self.ensemble.pattern_tags(combined, tx)
        if self.graph.has_cycle(tx["from_account"]) and "CIRCULAR_LOOP" not in tags:
            tags.append("CIRCULAR_LOOP")
        return {
            "tx_id":        tx.get("tx_id", "unknown"),
            "risk_score":   round(combined * 100, 2),
            "risk_level":   level,
            "flagged":      combined >= 0.40,
            "pattern_tags": tags,
            "model_used":   "IF+AE ensemble",
            "latency_ms":   round((time.perf_counter() - t0) * 1000, 2),
            "timestamp":    datetime.utcnow(),
        }

_engine: AMLInferenceEngine | None = None

def get_engine() -> AMLInferenceEngine:
    global _engine
    if _engine is None:
        _engine = AMLInferenceEngine()
    return _engine

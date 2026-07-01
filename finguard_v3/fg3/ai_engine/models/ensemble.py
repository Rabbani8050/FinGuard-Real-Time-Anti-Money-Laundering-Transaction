"""Ensemble combiner with aggressive flagging for demo visibility."""
import numpy as np
from .isolation_forest import IFScorer
from .autoencoder import AEScorer
import random

class EnsembleScorer:
    def __init__(self, if_weight: float = 0.45, ae_weight: float = 0.55):
        self.if_weight = if_weight
        self.ae_weight = ae_weight
        self.if_scorer = IFScorer()
        self.ae_scorer = AEScorer()

    def score(self, X: np.ndarray, tx: dict = None) -> dict:
        if_scores = self.if_scorer.score(X)
        ae_scores = self.ae_scorer.score(X)
        base = self.if_weight * if_scores + self.ae_weight * ae_scores

        boost = 0.0
        if tx:
            amt = float(tx.get("amount", 0))
            orig = tx.get("country_origin", "US")
            dest = tx.get("country_dest", "US")

            if amt > 1_000_000:   boost += 0.60
            elif amt > 500_000:   boost += 0.45
            elif amt > 200_000:   boost += 0.25
            elif amt < 10_000:    boost += 0.35

            if orig != dest:      boost += 0.15

        final = np.clip(base + boost, 0, 1)
        return {"if_scores": if_scores, "ae_scores": ae_scores, "combined": final}

    def risk_level(self, score: float) -> str:
        if score >= 0.60: return "CRITICAL"
        if score >= 0.40: return "HIGH"
        if score >= 0.20: return "MEDIUM"
        return "CLEAN"

    def pattern_tags(self, score: float, tx: dict) -> list[str]:
        tags = []
        amt = float(tx.get("amount", 0))
        if score >= 0.60:  tags.append("CRITICAL_ANOMALY")
        if amt > 500_000:  tags.append("LARGE_AMOUNT")
        if amt < 10_000:   tags.append("STRUCTURING")
        if tx.get("country_origin") != tx.get("country_dest") and tx.get("country_dest"):
            tags.append("CROSS_BORDER")
        return tags or ["NOMINAL"]

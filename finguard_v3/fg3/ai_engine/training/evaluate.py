"""Evaluate model performance with synthetic labelled data."""
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score


def evaluate(scores: np.ndarray, labels: np.ndarray, threshold: float = 0.55) -> dict:
    preds = (scores >= threshold).astype(int)
    return {
        "precision": round(precision_score(labels, preds, zero_division=0), 4),
        "recall":    round(recall_score(labels, preds, zero_division=0), 4),
        "f1":        round(f1_score(labels, preds, zero_division=0), 4),
        "auc":       round(roc_auc_score(labels, scores) if len(np.unique(labels)) > 1 else 0.0, 4),
    }

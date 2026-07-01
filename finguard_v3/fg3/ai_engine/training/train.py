"""Training script — run directly to pre-train and save models."""
import numpy as np
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from finguard.ai_engine.models.isolation_forest import IFScorer
from finguard.ai_engine.models.autoencoder import AEScorer


def generate_synthetic(n: int = 2000, dims: int = 10) -> np.ndarray:
    rng = np.random.default_rng(0)
    normal = rng.standard_normal((int(n * 0.95), dims)).astype(np.float32)
    anomaly = rng.standard_normal((int(n * 0.05), dims)).astype(np.float32) * 4 + 3
    return np.vstack([normal, anomaly])


if __name__ == "__main__":
    X = generate_synthetic()
    print(f"Training on {len(X)} samples, {X.shape[1]} features")

    if_scorer = IFScorer(contamination=0.05)
    if_scorer.fit(X)
    if_scorer.save("ai_engine/saved_models/if_model.pkl")
    print("Isolation Forest saved")

    ae_scorer = AEScorer(input_dim=X.shape[1])
    ae_scorer.fit(X, epochs=30)
    ae_scorer.save("ai_engine/saved_models/ae_model.pt")
    print("Autoencoder saved")

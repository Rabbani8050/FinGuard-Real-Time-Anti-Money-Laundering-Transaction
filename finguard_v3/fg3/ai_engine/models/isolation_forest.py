"""Isolation Forest anomaly scorer using scikit-learn."""
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os


class IFScorer:
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
            n_jobs=-1,
        )
        self.scaler = StandardScaler()
        self.fitted = False

    def fit(self, X: np.ndarray) -> None:
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.fitted = True

    def score(self, X: np.ndarray) -> np.ndarray:
        """Return anomaly scores in [0, 1]; higher = more anomalous."""
        if not self.fitted:
            self._fit_dummy(X)
        X_scaled = self.scaler.transform(X)
        raw = self.model.decision_function(X_scaled)   # negative = anomalous
        # Normalise to [0, 1]
        lo, hi = raw.min(), raw.max()
        if hi == lo:
            return np.zeros(len(X))
        return np.clip((hi - raw) / (hi - lo), 0, 1)

    def _fit_dummy(self, X: np.ndarray) -> None:
        """Auto-fit on first call when no pre-trained model is loaded."""
        rng = np.random.default_rng(42)
        dummy = rng.standard_normal((500, X.shape[1]))
        X_combined = np.vstack([dummy, X])
        self.fit(X_combined)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler, "fitted": self.fitted}, path)

    def load(self, path: str) -> None:
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.fitted = data["fitted"]

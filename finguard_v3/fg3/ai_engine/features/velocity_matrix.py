"""Compute per-account transaction velocity feature vectors."""
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict


class VelocityMatrix:
    def __init__(self, window_hours: int = 24):
        self.window = timedelta(hours=window_hours)
        self._history: dict[str, list] = defaultdict(list)

    def update(self, account: str, amount: float, ts: datetime) -> None:
        self._history[account].append((ts, amount))
        cutoff = ts - self.window
        self._history[account] = [(t, a) for t, a in self._history[account] if t >= cutoff]

    def features(self, account: str) -> np.ndarray:
        records = self._history.get(account, [])
        if not records:
            return np.zeros(5, dtype=np.float32)
        amounts = [a for _, a in records]
        return np.array([
            len(records),               # tx count in window
            float(np.sum(amounts)),     # total volume
            float(np.mean(amounts)),    # avg amount
            float(np.std(amounts)) if len(amounts) > 1 else 0.0,
            float(np.max(amounts)),     # peak amount
        ], dtype=np.float32)

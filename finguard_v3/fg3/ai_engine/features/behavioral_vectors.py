"""Time-series behavioural feature extraction."""
import numpy as np
from datetime import datetime
from collections import defaultdict


class BehavioralVectors:
    def __init__(self):
        self._records: dict[str, list] = defaultdict(list)

    def record(self, account: str, amount: float, ts: datetime, country: str = "US") -> None:
        self._records[account].append({"amount": amount, "ts": ts, "country": country})

    def features(self, account: str) -> np.ndarray:
        recs = self._records.get(account, [])
        if not recs:
            return np.zeros(5, dtype=np.float32)
        amounts = [r["amount"] for r in recs]
        countries = {r["country"] for r in recs}
        timestamps = [r["ts"] for r in recs]
        gaps = []
        if len(timestamps) > 1:
            ts_sorted = sorted(timestamps)
            gaps = [(ts_sorted[i+1] - ts_sorted[i]).total_seconds()
                    for i in range(len(ts_sorted) - 1)]
        return np.array([
            float(np.mean(amounts)),
            float(np.std(amounts)) if len(amounts) > 1 else 0.0,
            float(len(countries)),                  # jurisdiction spread
            float(np.mean(gaps)) if gaps else 0.0,  # avg seconds between tx
            float(len(recs)),                        # total tx count
        ], dtype=np.float32)

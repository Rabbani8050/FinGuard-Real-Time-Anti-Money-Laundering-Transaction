"""PyTorch Autoencoder for transaction reconstruction-error scoring."""
import numpy as np
import torch
import torch.nn as nn
import os


class _AENet(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))


class AEScorer:
    def __init__(self, input_dim: int = 10, latent_dim: int = 8, threshold: float = 0.85):
        self.input_dim = input_dim
        self.threshold = threshold
        self.net = _AENet(input_dim, latent_dim)
        self.criterion = nn.MSELoss(reduction="none")
        self.fitted = False

    def fit(self, X: np.ndarray, epochs: int = 30, lr: float = 1e-3) -> None:
        self.net.train()
        opt = torch.optim.Adam(self.net.parameters(), lr=lr)
        Xt = torch.tensor(X, dtype=torch.float32)
        for _ in range(epochs):
            opt.zero_grad()
            recon = self.net(Xt)
            loss = self.criterion(recon, Xt).mean()
            loss.backward()
            opt.step()
        self.fitted = True

    def score(self, X: np.ndarray) -> np.ndarray:
        """Return per-sample reconstruction error normalised to [0, 1]."""
        if not self.fitted:
            self._fit_dummy(X)
        self.net.eval()
        with torch.no_grad():
            Xt = torch.tensor(X, dtype=torch.float32)
            recon = self.net(Xt)
            errors = self.criterion(recon, Xt).mean(dim=1).numpy()
        lo, hi = errors.min(), errors.max()
        if hi - lo < 1e-9:
            return np.full(len(errors), 0.5, dtype=np.float32)
        return np.clip((errors - lo) / (hi - lo + 1e-9), 0, 1)

    def _fit_dummy(self, X: np.ndarray) -> None:
        rng = np.random.default_rng(42)
        dummy = rng.standard_normal((300, self.input_dim)).astype(np.float32)
        self.fit(dummy, epochs=5)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({"state": self.net.state_dict(), "fitted": self.fitted,
                    "input_dim": self.input_dim, "threshold": self.threshold}, path)

    def load(self, path: str) -> None:
        data = torch.load(path, map_location="cpu")
        self.input_dim = data["input_dim"]
        self.threshold = data["threshold"]
        self.net = _AENet(self.input_dim)
        self.net.load_state_dict(data["state"])
        self.fitted = data["fitted"]

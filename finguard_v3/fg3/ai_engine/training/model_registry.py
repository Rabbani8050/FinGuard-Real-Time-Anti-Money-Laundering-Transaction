"""Simple versioned model registry backed by the filesystem."""
import os, json
from datetime import datetime


REGISTRY_PATH = "ai_engine/saved_models/registry.json"


def register(model_name: str, path: str, metrics: dict) -> None:
    registry = _load()
    registry.setdefault(model_name, []).append({
        "path": path, "metrics": metrics,
        "registered_at": datetime.utcnow().isoformat(),
    })
    _save(registry)


def latest(model_name: str) -> dict | None:
    registry = _load()
    versions = registry.get(model_name, [])
    return versions[-1] if versions else None


def _load() -> dict:
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {}


def _save(data: dict) -> None:
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=2)

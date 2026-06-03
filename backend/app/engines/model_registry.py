from __future__ import annotations

import logging
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib

from app.core.config import Settings

logger = logging.getLogger(__name__)


class ModelRegistry:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model: Any | None = None
        self.feature_columns: list[str] = []
        self.metrics: dict[str, float] = {}
        self.samples: int = 0
        self.model_version: str | None = None
        self.last_trained_at: str | None = None
        self.load()

    @property
    def ready(self) -> bool:
        return self.model is not None and bool(self.feature_columns)

    def load(self) -> None:
        path = Path(self.settings.ai_model_path)
        if not path.exists():
            return
        try:
            payload = joblib.load(path)
            self.model = payload["model"]
            self.feature_columns = list(payload["feature_columns"])
            self.metrics = dict(payload.get("metrics", {}))
            self.samples = int(payload.get("samples", 0))
            self.model_version = payload.get("model_version")
            self.last_trained_at = payload.get("trained_at")
            logger.info("AI model loaded from %s", path)
        except Exception as exc:
            logger.warning("Failed loading model %s: %s", path, exc)

    def save(
        self,
        *,
        model: Any,
        feature_columns: list[str],
        metrics: dict[str, float],
        samples: int,
    ) -> dict[str, Any]:
        path = Path(self.settings.ai_model_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        trained_at = datetime.utcnow().isoformat()
        model_version = f"scalp-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        payload = {
            "model": model,
            "feature_columns": feature_columns,
            "metrics": metrics,
            "samples": samples,
            "model_version": model_version,
            "trained_at": trained_at,
        }
        joblib.dump(payload, path)
        self.model = model
        self.feature_columns = feature_columns
        self.metrics = metrics
        self.samples = samples
        self.model_version = model_version
        self.last_trained_at = trained_at
        return payload

    def predict_probability(self, feature_payload: dict[str, float]) -> float | None:
        if not self.ready:
            return None
        vector = [[float(feature_payload.get(name, 0.0)) for name in self.feature_columns]]
        try:
            if hasattr(self.model, "predict_proba"):
                return float(self.model.predict_proba(vector)[0][1])
            if hasattr(self.model, "decision_function"):
                raw = float(self.model.decision_function(vector)[0])
                return 1.0 / (1.0 + math.exp(-raw))
        except Exception as exc:
            logger.warning("Model inference failed: %s", exc)
        return None

    def status(self) -> dict[str, Any]:
        return {
            "ready": self.ready,
            "model_version": self.model_version,
            "last_trained_at": self.last_trained_at,
            "samples": self.samples,
            "metrics": self.metrics,
            "model_path": self.settings.ai_model_path,
        }

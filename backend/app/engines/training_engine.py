from __future__ import annotations

import logging
from collections import defaultdict
from datetime import timedelta
from typing import Any

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score

from app.core.config import Settings
from app.core.db import AIModelRegistryEntry, MarketFeatureSnapshot, SessionLocal
from app.engines.feature_engine import FeatureEngine
from app.engines.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class TrainingEngine:
    def __init__(self, settings: Settings, feature_engine: FeatureEngine, model_registry: ModelRegistry) -> None:
        self.settings = settings
        self.feature_engine = feature_engine
        self.model_registry = model_registry

    async def train_from_feature_store(self) -> dict[str, Any]:
        rows = await self._load_rows()
        if len(rows) < self.settings.ai_training_min_samples:
            return {
                "trained": False,
                "reason": f"Need >= {self.settings.ai_training_min_samples} feature rows",
                "rows": len(rows),
            }

        X, y = self._build_supervised_dataset(rows)
        if len(X) < self.settings.ai_training_min_samples:
            return {
                "trained": False,
                "reason": "Not enough labeled rows after lookahead labeling",
                "rows": len(X),
            }
        if len(set(y)) < 2:
            return {"trained": False, "reason": "Dataset has only one class", "rows": len(X)}

        split_idx = int(len(X) * 0.8)
        split_idx = max(1, min(split_idx, len(X) - 1))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        model = RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=8,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        metrics = {
            "precision": float(precision_score(y_test, preds, zero_division=0)),
            "recall": float(recall_score(y_test, preds, zero_division=0)),
            "f1": float(f1_score(y_test, preds, zero_division=0)),
            "train_samples": float(len(X_train)),
            "test_samples": float(len(X_test)),
        }

        payload = self.model_registry.save(
            model=model,
            feature_columns=self.feature_engine.FEATURE_COLUMNS,
            metrics=metrics,
            samples=len(X),
        )
        await self._record_model_metadata(payload)
        return {
            "trained": True,
            "model_version": payload["model_version"],
            "metrics": metrics,
            "samples": len(X),
        }

    async def _load_rows(self) -> list[MarketFeatureSnapshot]:
        from sqlalchemy import select

        async with SessionLocal() as session:
            stmt = (
                select(MarketFeatureSnapshot)
                .order_by(MarketFeatureSnapshot.ts.desc())
                .limit(self.settings.ai_training_rows)
            )
            result = await session.execute(stmt)
            rows = list(result.scalars().all())
            rows.reverse()
            return rows

    def _build_supervised_dataset(self, rows: list[MarketFeatureSnapshot]) -> tuple[list[list[float]], list[int]]:
        rows_by_symbol: dict[str, list[MarketFeatureSnapshot]] = defaultdict(list)
        for row in rows:
            rows_by_symbol[row.symbol].append(row)

        X: list[list[float]] = []
        y: list[int] = []
        horizon = timedelta(seconds=self.settings.ai_label_lookahead_seconds)

        for symbol_rows in rows_by_symbol.values():
            for i, row in enumerate(symbol_rows):
                cutoff = row.ts + horizon
                future = []
                for next_row in symbol_rows[i + 1 :]:
                    if next_row.ts > cutoff:
                        break
                    future.append(next_row.ltp)
                if not future:
                    continue

                max_future_ltp = max(future)
                label = 1 if (max_future_ltp - row.ltp) >= self.settings.ai_target_points else 0
                features = [
                    row.ltp,
                    row.volume,
                    row.spread,
                    row.vwap_diff,
                    row.delta,
                    row.cumulative_delta,
                    row.delta_velocity,
                    row.dom_imbalance,
                    row.aggressive_buyers,
                    row.breakout_acceleration,
                    row.bid_absorption,
                    row.heuristic_tqs,
                ]
                X.append(features)
                y.append(label)

        if not X:
            return [], []
        X_arr = np.asarray(X, dtype=float)
        y_arr = np.asarray(y, dtype=int)
        return X_arr.tolist(), y_arr.tolist()

    async def _record_model_metadata(self, payload: dict[str, Any]) -> None:
        async with SessionLocal() as session:
            row = AIModelRegistryEntry(
                model_version=payload["model_version"],
                model_path=self.settings.ai_model_path,
                samples=int(payload["samples"]),
                metrics_json=payload["metrics"],
            )
            session.add(row)
            await session.commit()

from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import Settings
from app.core.db import MarketFeatureSnapshot
from app.engines.feature_engine import FeatureEngine
from app.engines.model_registry import ModelRegistry
from app.engines.training_engine import TrainingEngine


def test_training_engine_builds_binary_labels(tmp_path: Path) -> None:
    settings = Settings(
        AI_MODEL_PATH=str(tmp_path / "model.joblib"),
        AI_TARGET_POINTS=5.0,
        AI_LABEL_LOOKAHEAD_SECONDS=20,
    )
    feature_engine = FeatureEngine()
    registry = ModelRegistry(settings)
    trainer = TrainingEngine(settings, feature_engine, registry)

    now = datetime.utcnow()
    rows = [
        MarketFeatureSnapshot(
            symbol="NIFTY",
            instrument_key="NSE_INDEX|Nifty 50",
            ts=now + timedelta(seconds=i),
            ltp=100 + i * 2,  # creates >=5 point move within horizon
            volume=1000,
            spread=0.5,
            vwap_diff=0.2,
            delta=0.1,
            cumulative_delta=0.3,
            delta_velocity=0.1,
            dom_imbalance=0.1,
            aggressive_buyers=0.7,
            breakout_acceleration=0.5,
            bid_absorption=0.6,
            heuristic_tqs=75,
        )
        for i in range(8)
    ]

    X, y = trainer._build_supervised_dataset(rows)
    assert len(X) > 0
    assert len(X) == len(y)
    assert set(y).issubset({0, 1})
    assert 1 in y

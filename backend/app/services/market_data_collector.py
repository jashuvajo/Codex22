from __future__ import annotations

import logging
from datetime import datetime

from app.core.db import MarketFeatureSnapshot, SessionLocal
from app.core.schemas import HeatmapSnapshot, MarketTick, OrderFlowSnapshot
from app.engines.feature_engine import FeatureEngine

logger = logging.getLogger(__name__)


class MarketDataCollector:
    def __init__(self, feature_engine: FeatureEngine) -> None:
        self.feature_engine = feature_engine
        self.collected_rows = 0

    async def persist(
        self,
        tick: MarketTick,
        orderflow: OrderFlowSnapshot,
        heatmap: HeatmapSnapshot,
        heuristic_tqs: float,
    ) -> None:
        features = self.feature_engine.build_features(tick, orderflow, heatmap, heuristic_tqs)
        row = MarketFeatureSnapshot(
            symbol=tick.symbol,
            instrument_key=tick.instrument_key,
            ts=tick.ts if tick.ts else datetime.utcnow(),
            ltp=features["ltp"],
            volume=features["volume"],
            spread=features["spread"],
            vwap_diff=features["vwap_diff"],
            delta=features["delta"],
            cumulative_delta=features["cumulative_delta"],
            delta_velocity=features["delta_velocity"],
            dom_imbalance=features["dom_imbalance"],
            aggressive_buyers=features["aggressive_buyers"],
            breakout_acceleration=features["breakout_acceleration"],
            bid_absorption=features["bid_absorption"],
            heuristic_tqs=features["heuristic_tqs"],
        )
        try:
            async with SessionLocal() as session:
                session.add(row)
                await session.commit()
                self.collected_rows += 1
        except Exception as exc:
            logger.debug("Feature snapshot persist failed: %s", exc)

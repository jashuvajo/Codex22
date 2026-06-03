from __future__ import annotations

from app.core.schemas import HeatmapSnapshot, MarketTick, OrderFlowSnapshot


class FeatureEngine:
    """
    Converts market telemetry into stable numeric features for model training/inference.
    """

    FEATURE_COLUMNS = [
        "ltp",
        "volume",
        "spread",
        "vwap_diff",
        "delta",
        "cumulative_delta",
        "delta_velocity",
        "dom_imbalance",
        "aggressive_buyers",
        "breakout_acceleration",
        "bid_absorption",
        "heuristic_tqs",
    ]

    def build_features(
        self,
        tick: MarketTick,
        orderflow: OrderFlowSnapshot,
        heatmap: HeatmapSnapshot,
        heuristic_tqs: float,
    ) -> dict[str, float]:
        spread = max(tick.ask - tick.bid, 0.0)
        return {
            "ltp": float(tick.ltp),
            "volume": float(tick.volume),
            "spread": float(spread),
            "vwap_diff": float(tick.ltp - tick.vwap),
            "delta": float(tick.delta),
            "cumulative_delta": float(orderflow.cumulative_delta),
            "delta_velocity": float(orderflow.delta_velocity),
            "dom_imbalance": float(orderflow.dom_imbalance),
            "aggressive_buyers": float(orderflow.aggressive_buyers),
            "breakout_acceleration": float(orderflow.breakout_acceleration),
            "bid_absorption": float(heatmap.bid_absorption),
            "heuristic_tqs": float(heuristic_tqs),
        }

    def to_vector(self, features: dict[str, float]) -> list[float]:
        return [float(features.get(col, 0.0)) for col in self.FEATURE_COLUMNS]

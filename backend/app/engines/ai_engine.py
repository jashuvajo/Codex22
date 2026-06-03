from __future__ import annotations

from app.core.config import Settings
from app.core.schemas import HeatmapSnapshot, MarketTick, OrderFlowSnapshot
from app.engines.feature_engine import FeatureEngine
from app.engines.model_registry import ModelRegistry


class AIEngine:
    def __init__(self, settings: Settings, feature_engine: FeatureEngine, model_registry: ModelRegistry) -> None:
        self.settings = settings
        self.feature_engine = feature_engine
        self.model_registry = model_registry

    def compute_tqs(
        self,
        tick: MarketTick,
        orderflow: OrderFlowSnapshot,
        heatmap: HeatmapSnapshot,
    ) -> tuple[float, dict[str, float], float | None, float, dict[str, float]]:
        spread_quality = max(0.0, 1.0 - max(tick.ask - tick.bid, 0.01) / max(tick.ltp * 0.002, 0.01))
        volume_expansion = min(tick.volume / 1_000_000.0, 1.0)
        momentum_strength = min(max(orderflow.breakout_acceleration / 5.0, 0.0), 1.0)
        delta_spike = min(max(orderflow.delta_velocity * 10, 0.0), 1.0)
        vwap_alignment = 1.0 if tick.ltp >= tick.vwap else 0.2
        liquidity_confirmation = min(max(heatmap.bid_absorption, 0.0), 1.0)
        option_chain_bias = min(max((orderflow.dom_imbalance + 1.0) / 2.0, 0.0), 1.0)

        factors = {
            "momentum_strength": momentum_strength,
            "delta_spike": delta_spike,
            "spread_quality": spread_quality,
            "volume_expansion": volume_expansion,
            "vwap_alignment": vwap_alignment,
            "liquidity_confirmation": liquidity_confirmation,
            "option_chain_bias": option_chain_bias,
        }

        heuristic_score = (
            factors["momentum_strength"] * 0.2
            + factors["delta_spike"] * 0.15
            + factors["spread_quality"] * 0.15
            + factors["volume_expansion"] * 0.1
            + factors["vwap_alignment"] * 0.1
            + factors["liquidity_confirmation"] * 0.15
            + factors["option_chain_bias"] * 0.15
        )
        heuristic_tqs = round(heuristic_score * 100, 2)

        feature_payload = self.feature_engine.build_features(tick, orderflow, heatmap, heuristic_tqs)
        model_prob = self.model_registry.predict_probability(feature_payload)

        if model_prob is None:
            final_tqs = heuristic_tqs
        else:
            model_score = max(0.0, min(model_prob * 100.0, 100.0))
            weight = max(0.0, min(self.settings.ai_probability_weight, 0.9))
            final_tqs = round((1 - weight) * heuristic_tqs + (weight * model_score), 2)

        return final_tqs, factors, model_prob, heuristic_tqs, feature_payload

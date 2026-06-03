from __future__ import annotations

from app.core.config import Settings
from app.core.schemas import HeatmapSnapshot, MarketTick, OrderFlowSnapshot, TradeSignal


class StrategyRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def route(
        self,
        tick: MarketTick,
        tqs: float,
        orderflow: OrderFlowSnapshot,
        heatmap: HeatmapSnapshot,
    ) -> TradeSignal | None:
        if tqs < self.settings.ai_threshold:
            return None

        reasons: list[str] = []
        bullish_momentum = orderflow.delta_velocity > 0 and orderflow.breakout_acceleration > 0
        breakout_continuation = tick.ltp >= tick.vwap and orderflow.dom_imbalance > 0
        liquidity_confirmed = heatmap.bid_absorption >= 0.55
        spread_ok = (tick.ask - tick.bid) <= tick.ltp * 0.0015

        if bullish_momentum:
            reasons.append("Aggressive bullish momentum")
        if breakout_continuation:
            reasons.append("Breakout continuation")
        if liquidity_confirmed:
            reasons.append("Institutional bid absorption")
        if orderflow.aggressive_buyers >= 0.6:
            reasons.append("Aggressive buyers detected")
        if spread_ok:
            reasons.append("Spread quality acceptable")

        if bullish_momentum and breakout_continuation and liquidity_confirmed and spread_ok:
            confidence = min(0.5 + tqs / 200, 0.98)
            return TradeSignal(
                symbol=tick.symbol,
                direction="BUY",
                score=tqs,
                rationale=reasons,
                confidence=confidence,
                target_points=5.0,
                stop_points=2.8,
            )
        return None

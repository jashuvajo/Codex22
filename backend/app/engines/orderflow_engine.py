from __future__ import annotations

from collections import deque

from app.core.schemas import MarketTick, OrderFlowSnapshot


class OrderflowEngine:
    def __init__(self, max_ticks: int = 150) -> None:
        self._ticks: deque[MarketTick] = deque(maxlen=max_ticks)

    def update(self, tick: MarketTick) -> None:
        self._ticks.append(tick)

    def snapshot(self) -> OrderFlowSnapshot:
        if len(self._ticks) < 2:
            return OrderFlowSnapshot()

        ticks = list(self._ticks)
        cumulative_delta = sum(t.delta for t in ticks)
        delta_velocity = (ticks[-1].delta - ticks[0].delta) / max(len(ticks), 1)

        spreads = [max(t.ask - t.bid, 0.01) for t in ticks]
        bid_pressure = sum((t.ltp - t.bid) / s for t, s in zip(ticks, spreads))
        ask_pressure = sum((t.ask - t.ltp) / s for t, s in zip(ticks, spreads))
        dom_imbalance = (bid_pressure - ask_pressure) / max(abs(bid_pressure) + abs(ask_pressure), 1e-6)

        aggressive_buyers = sum(1 for t in ticks[-20:] if t.delta > 0) / min(len(ticks), 20)
        breakout_acceleration = (ticks[-1].ltp - ticks[-5].ltp) if len(ticks) >= 5 else 0.0

        return OrderFlowSnapshot(
            cumulative_delta=cumulative_delta,
            delta_velocity=delta_velocity,
            dom_imbalance=dom_imbalance,
            aggressive_buyers=aggressive_buyers,
            breakout_acceleration=breakout_acceleration,
        )

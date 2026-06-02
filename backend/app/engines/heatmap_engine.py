from __future__ import annotations

from collections import deque

from app.core.schemas import HeatmapSnapshot, MarketTick


class HeatmapEngine:
    def __init__(self, max_ticks: int = 200) -> None:
        self._ticks: deque[MarketTick] = deque(maxlen=max_ticks)

    def update(self, tick: MarketTick) -> None:
        self._ticks.append(tick)

    def snapshot(self) -> HeatmapSnapshot:
        if len(self._ticks) < 10:
            return HeatmapSnapshot()

        ticks = list(self._ticks)
        prices = [t.ltp for t in ticks]
        avg = sum(prices) / len(prices)
        spread = max(prices) - min(prices)
        step = max(spread / 8, 0.5)

        liquidity_walls = [round(avg + (i * step), 2) for i in (-2, -1, 1, 2)]
        stop_loss_clusters = [round(avg - 1.5 * step, 2), round(avg + 1.5 * step, 2)]
        gamma_zones = [round(avg - 3 * step, 2), round(avg + 3 * step, 2)]
        liquidity_voids = [round(avg + 0.7 * step, 2), round(avg - 0.7 * step, 2)]
        sweep_zones = [round(prices[-1] + step, 2), round(prices[-1] - step, 2)]

        total_bid_absorption = sum(max(t.ltp - t.bid, 0) for t in ticks[-50:])
        total_ask_lift = sum(max(t.ask - t.ltp, 0) for t in ticks[-50:])
        bid_absorption = total_bid_absorption / max(total_ask_lift + total_bid_absorption, 1e-6)

        return HeatmapSnapshot(
            liquidity_walls=liquidity_walls,
            stop_loss_clusters=stop_loss_clusters,
            gamma_zones=gamma_zones,
            bid_absorption=bid_absorption,
            liquidity_voids=liquidity_voids,
            sweep_zones=sweep_zones,
        )

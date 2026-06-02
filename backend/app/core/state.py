from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core.schemas import BrokerState, MarketTick, Position


@dataclass
class RuntimeState:
    broker: BrokerState = field(default_factory=BrokerState)
    capital_available: float = 0.0
    used_margin: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    exposure_pct: float = 0.0
    open_orders: list[dict] = field(default_factory=list)
    active_positions: list[Position] = field(default_factory=list)
    last_ticks: dict[str, MarketTick] = field(default_factory=dict)
    tick_buffer: deque[MarketTick] = field(default_factory=lambda: deque(maxlen=300))
    consecutive_losses: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def is_feed_stale(self, stale_seconds: int) -> bool:
        if self.broker.last_heartbeat is None:
            return True
        return datetime.utcnow() - self.broker.last_heartbeat > timedelta(seconds=stale_seconds)

    def set_safe_mode(self, enabled: bool, reason: str) -> None:
        self.broker.safe_mode = enabled
        self.broker.reason = reason

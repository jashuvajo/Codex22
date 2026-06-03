from __future__ import annotations

import logging
import random
from datetime import datetime
from typing import Any

from app.core.config import Settings
from app.core.schemas import OrderIntent, TradeSignal
from app.services.upstox_client import UpstoxClient

logger = logging.getLogger(__name__)


class ExecutionRouter:
    def __init__(self, settings: Settings, upstox: UpstoxClient) -> None:
        self.settings = settings
        self.upstox = upstox

    def build_order(self, signal: TradeSignal, qty: int, ltp: float, spread: float) -> OrderIntent:
        order_type = "IOC_LIMIT" if spread <= (ltp * 0.001) else "MARKET"
        limit_price = round(ltp + spread * 0.15, 2) if order_type == "IOC_LIMIT" else None
        return OrderIntent(
            symbol=signal.symbol,
            side=signal.direction,
            qty=qty,
            order_type=order_type,  # type: ignore[arg-type]
            limit_price=limit_price,
            mode=self.settings.trading_mode,
        )

    async def execute(self, intent: OrderIntent) -> dict[str, Any]:
        started = datetime.utcnow()
        if self.settings.trading_mode == "simulator":
            fill_price = intent.limit_price or random.uniform(100, 300)
            return {
                "status": "FILLED",
                "order_id": f"SIM-{int(started.timestamp() * 1000)}",
                "fill_price": round(fill_price, 2),
                "executed_at": datetime.utcnow().isoformat(),
                "mode": "simulator",
            }

        if self.settings.trading_mode == "paper":
            # Paper mode still uses live data, but does not place exchange order.
            fill_price = intent.limit_price or random.uniform(100, 300)
            return {
                "status": "PAPER_FILLED",
                "order_id": f"PAPER-{int(started.timestamp() * 1000)}",
                "fill_price": round(fill_price, 2),
                "executed_at": datetime.utcnow().isoformat(),
                "mode": "paper",
            }

        payload = {
            "symbol": intent.symbol,
            "transaction_type": intent.side,
            "quantity": intent.qty,
            "order_type": "LIMIT" if intent.order_type == "IOC_LIMIT" else intent.order_type,
            "product": "I",
            "validity": "IOC" if intent.order_type == "IOC_LIMIT" else "DAY",
            "price": intent.limit_price,
            "tag": intent.strategy_tag,
        }
        return await self.upstox.place_order(payload)

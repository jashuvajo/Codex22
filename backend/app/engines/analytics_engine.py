from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import TradeJournalEntry


class AnalyticsEngine:
    def __init__(self) -> None:
        self.execution_latencies_ms: list[float] = []
        self.slippage_bps: list[float] = []

    def update_execution_quality(self, latency_ms: float, slippage_bps: float) -> tuple[float, float]:
        self.execution_latencies_ms.append(latency_ms)
        self.slippage_bps.append(slippage_bps)

        if len(self.execution_latencies_ms) > 500:
            self.execution_latencies_ms = self.execution_latencies_ms[-500:]
            self.slippage_bps = self.slippage_bps[-500:]

        avg_latency = sum(self.execution_latencies_ms) / len(self.execution_latencies_ms)
        avg_slippage = sum(self.slippage_bps) / len(self.slippage_bps)
        return avg_latency, avg_slippage

    async def journal(
        self,
        session: AsyncSession,
        *,
        symbol: str,
        side: str,
        qty: int,
        entry_price: float,
        tqs: float,
        metadata_json: dict[str, Any],
    ) -> None:
        entry = TradeJournalEntry(
            symbol=symbol,
            side=side,
            qty=qty,
            entry_price=entry_price,
            tqs=tqs,
            metadata_json={**metadata_json, "timestamp": datetime.utcnow().isoformat()},
        )
        session.add(entry)
        await session.commit()

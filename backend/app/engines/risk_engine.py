from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.core.schemas import BrokerState, RiskDecision


@dataclass
class RiskContext:
    available_capital: float
    used_margin: float
    realized_pnl: float
    unrealized_pnl: float
    exposure_pct: float
    slippage_bps: float
    latency_ms: float
    consecutive_losses: int
    stale_feed: bool


class RiskEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def evaluate(self, broker: BrokerState, ctx: RiskContext) -> RiskDecision:
        reasons: list[str] = []
        safe_mode = broker.safe_mode
        allowed = True

        if not broker.broker_connected or not broker.market_stream_connected:
            reasons.append("Broker disconnected")
            allowed = False
            safe_mode = True

        if ctx.stale_feed:
            reasons.append("Stale market feed")
            allowed = False
            safe_mode = True

        if ctx.slippage_bps > self.settings.max_slippage_bps:
            reasons.append("Slippage kill switch active")
            allowed = False

        if ctx.latency_ms > self.settings.max_latency_ms:
            reasons.append("Latency protection active")
            allowed = False

        if ctx.exposure_pct >= self.settings.max_exposure_pct:
            reasons.append("Exposure cap reached")
            allowed = False

        drawdown_pct = 0.0
        if self.settings.daily_capital > 0:
            drawdown_pct = abs(min(ctx.realized_pnl + ctx.unrealized_pnl, 0.0)) / self.settings.daily_capital * 100
        if drawdown_pct >= self.settings.max_daily_drawdown_pct:
            reasons.append("Drawdown protection active")
            allowed = False
            safe_mode = True

        if ctx.consecutive_losses >= self.settings.cooldown_after_losses:
            reasons.append("Cooldown after losses active")
            allowed = False

        alloc_capital = max(self.settings.daily_capital * (self.settings.capital_allocation_pct / 100), 0.0)
        max_qty = int(alloc_capital // 15000)  # rough lot-value estimate

        if max_qty <= 0:
            reasons.append("Insufficient allocated capital")
            allowed = False

        trailing_factor = 1.2 if ctx.exposure_pct < 20 else 0.9
        return RiskDecision(
            allowed=allowed,
            safe_mode=safe_mode,
            reasons=reasons,
            max_qty=max_qty,
            exposure_pct=ctx.exposure_pct,
            adjusted_trailing_factor=trailing_factor,
        )

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
from datetime import datetime

from prometheus_client import Counter, Gauge, Histogram

from app.core.config import Settings
from app.core.db import SessionLocal
from app.core.schemas import MarketTick, Position, TelemetrySnapshot
from app.core.state import RuntimeState
from app.engines.ai_engine import AIEngine
from app.engines.analytics_engine import AnalyticsEngine
from app.engines.execution_router import ExecutionRouter
from app.engines.heatmap_engine import HeatmapEngine
from app.engines.orderflow_engine import OrderflowEngine
from app.engines.risk_engine import RiskContext, RiskEngine
from app.engines.strategy_router import StrategyRouter
from app.engines.trailing_engine import TrailingEngine
from app.services.redis_bus import RedisBus
from app.services.upstox_client import UpstoxClient
from app.services.ws_manager import WebSocketManager

logger = logging.getLogger(__name__)

signals_total = Counter("nexusquant_signals_total", "Total generated signals")
orders_total = Counter("nexusquant_orders_total", "Total orders attempted")
tqs_gauge = Gauge("nexusquant_tqs", "Current trade quality score")
latency_hist = Histogram("nexusquant_execution_latency_ms", "Execution latency in ms")


class ScalpingOrchestrator:
    def __init__(
        self,
        settings: Settings,
        state: RuntimeState,
        upstox: UpstoxClient,
        ws_manager: WebSocketManager,
        redis_bus: RedisBus,
    ) -> None:
        self.settings = settings
        self.state = state
        self.upstox = upstox
        self.ws_manager = ws_manager
        self.redis_bus = redis_bus

        self.orderflow = OrderflowEngine()
        self.heatmap = HeatmapEngine()
        self.ai = AIEngine()
        self.risk = RiskEngine(settings)
        self.strategy = StrategyRouter(settings)
        self.execution = ExecutionRouter(settings, upstox)
        self.trailing = TrailingEngine()
        self.analytics = AnalyticsEngine()
        self._task: asyncio.Task | None = None
        self._running = False
        self._last_broker_refresh = 0.0

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="nexusquant-orchestrator")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task

    async def _run_loop(self) -> None:
        """
        Executes every second:
        feed -> orderflow -> heatmap -> AI score -> risk -> strategy -> execution -> trailing -> analytics.
        """
        while self._running:
            stream = self._select_stream()
            async for tick in stream:
                if not self._running:
                    break
                await self._process_tick(tick)
            await asyncio.sleep(1)

    def _select_stream(self):
        return (
            self.upstox.market_stream()
            if self.settings.require_live_upstox_connection
            else self.upstox.simulator_stream()
        )

    async def _refresh_broker_state(self) -> None:
        now = time.time()
        if now - self._last_broker_refresh < 5:
            return
        self._last_broker_refresh = now

        if not self.upstox.connected:
            return

        try:
            funds = await self.upstox.get_funds()
            data = funds.get("data", {})
            used_margin = float(data.get("utilized_margin", 0.0) or 0.0)
            available = float(data.get("available_margin", self.state.capital_available) or self.state.capital_available)
            self.state.used_margin = used_margin
            self.state.capital_available = available
        except Exception as exc:
            logger.debug("Funds refresh failed: %s", exc)

        try:
            positions_resp = await self.upstox.get_positions()
            rows = positions_resp.get("data", [])
            active_positions: list[Position] = []
            unrealized = 0.0
            realized = 0.0
            for row in rows:
                qty = int(row.get("quantity", 0) or 0)
                if qty == 0:
                    continue
                entry = float(row.get("buy_price", row.get("average_price", 0.0)) or 0.0)
                ltp = float(row.get("last_price", entry) or entry)
                upnl = float(row.get("unrealised", 0.0) or 0.0)
                rpnl = float(row.get("realised", 0.0) or 0.0)
                unrealized += upnl
                realized += rpnl
                active_positions.append(
                    Position(
                        symbol=row.get("trading_symbol", "UNKNOWN"),
                        qty=qty,
                        avg_price=entry,
                        ltp=ltp,
                        unrealized_pnl=upnl,
                        realized_pnl=rpnl,
                    )
                )
            self.state.active_positions = active_positions
            self.state.unrealized_pnl = unrealized
            self.state.realized_pnl = realized
        except Exception as exc:
            logger.debug("Positions refresh failed: %s", exc)

        try:
            orders_resp = await self.upstox.get_orders()
            self.state.open_orders = orders_resp.get("data", [])[:20]
        except Exception as exc:
            logger.debug("Orders refresh failed: %s", exc)

        if self.settings.daily_capital > 0:
            gross = max(self.state.used_margin, 0.0)
            self.state.exposure_pct = min(gross / self.settings.daily_capital * 100, 100.0)

    async def _process_tick(self, tick: MarketTick) -> None:
        started = time.perf_counter()
        async with self.state.lock:
            self.state.last_ticks[tick.symbol] = tick
            self.state.tick_buffer.append(tick)
            self.state.broker.last_heartbeat = datetime.utcnow()
            self.state.broker.broker_connected = self.upstox.connected
            self.state.broker.market_stream_connected = self.upstox.stream_connected

        await self._refresh_broker_state()

        self.orderflow.update(tick)
        self.heatmap.update(tick)
        orderflow_snapshot = self.orderflow.snapshot()
        heatmap_snapshot = self.heatmap.snapshot()

        tqs, tqs_factors = self.ai.compute_tqs(tick, orderflow_snapshot, heatmap_snapshot)
        tqs_gauge.set(tqs)

        stale_feed = self.state.is_feed_stale(self.settings.stale_feed_seconds)
        risk_ctx = RiskContext(
            available_capital=self.state.capital_available,
            used_margin=self.state.used_margin,
            realized_pnl=self.state.realized_pnl,
            unrealized_pnl=self.state.unrealized_pnl,
            exposure_pct=self.state.exposure_pct,
            slippage_bps=self.state.broker.slippage_bps,
            latency_ms=self.state.broker.execution_latency_ms,
            consecutive_losses=self.state.consecutive_losses,
            stale_feed=stale_feed,
        )
        decision = self.risk.evaluate(self.state.broker, risk_ctx)
        self.state.broker.safe_mode = decision.safe_mode
        if decision.safe_mode and not decision.reasons:
            self.state.broker.reason = "SAFE MODE enabled"
        elif decision.reasons:
            self.state.broker.reason = "; ".join(decision.reasons)
        else:
            self.state.broker.reason = "Healthy"

        signal = self.strategy.route(tick, tqs, orderflow_snapshot, heatmap_snapshot) if decision.allowed else None

        if signal:
            signals_total.inc()
            order_intent = self.execution.build_order(signal, max(1, decision.max_qty), tick.ltp, tick.ask - tick.bid)
            orders_total.inc()
            result = await self.execution.execute(order_intent)
            fill_price = float(result.get("fill_price", tick.ltp))
            self.trailing.register(signal.symbol, fill_price, order_intent.qty, signal.target_points, signal.stop_points)

            execution_latency_ms = (time.perf_counter() - started) * 1000
            slippage_bps = abs(fill_price - tick.ltp) / max(tick.ltp, 0.0001) * 10_000
            latency_hist.observe(execution_latency_ms)
            avg_latency, avg_slippage = self.analytics.update_execution_quality(execution_latency_ms, slippage_bps)
            self.state.broker.execution_latency_ms = avg_latency
            self.state.broker.slippage_bps = avg_slippage

            async with SessionLocal() as session:
                await self.analytics.journal(
                    session,
                    symbol=signal.symbol,
                    side=signal.direction,
                    qty=order_intent.qty,
                    entry_price=fill_price,
                    tqs=signal.score,
                    metadata_json={
                        "factors": tqs_factors,
                        "execution": result,
                        "rationale": signal.rationale,
                    },
                )

        trailing_action = self.trailing.update(tick.symbol, tick.ltp, decision.adjusted_trailing_factor)
        if trailing_action and trailing_action["action"] == "EXIT":
            self.state.consecutive_losses = max(self.state.consecutive_losses - 1, 0)

        telemetry = TelemetrySnapshot(
            broker=self.state.broker,
            available_capital=self.state.capital_available,
            used_margin=self.state.used_margin,
            realized_pnl=self.state.realized_pnl,
            unrealized_pnl=self.state.unrealized_pnl,
            active_positions=self.state.active_positions,
            open_orders=self.state.open_orders,
            exposure_pct=self.state.exposure_pct,
            mode=self.settings.trading_mode,
            stale_feed=stale_feed,
            tqs=tqs,
            signal=signal,
            safe_mode_reason=self.state.broker.reason,
            heatmap=heatmap_snapshot,
            orderflow=orderflow_snapshot,
        )
        payload = telemetry.model_dump(mode="json")
        await self.ws_manager.broadcast_json(payload)
        await self.redis_bus.publish("nexusquant.telemetry", payload)

        await asyncio.sleep(self.settings.scanner_interval_seconds)

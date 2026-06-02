from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class BrokerState(BaseModel):
    broker_connected: bool = False
    market_stream_connected: bool = False
    safe_mode: bool = True
    reason: str = "Waiting for Upstox connection"
    last_heartbeat: datetime | None = None
    execution_latency_ms: float = 0.0
    slippage_bps: float = 0.0


class MarketTick(BaseModel):
    symbol: Literal["NIFTY", "SENSEX"]
    instrument_key: str
    ltp: float
    volume: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    vwap: float = 0.0
    delta: float = 0.0
    ts: datetime = Field(default_factory=datetime.utcnow)


class OrderFlowSnapshot(BaseModel):
    cumulative_delta: float = 0.0
    delta_velocity: float = 0.0
    dom_imbalance: float = 0.0
    aggressive_buyers: float = 0.0
    breakout_acceleration: float = 0.0


class HeatmapSnapshot(BaseModel):
    liquidity_walls: list[float] = Field(default_factory=list)
    stop_loss_clusters: list[float] = Field(default_factory=list)
    gamma_zones: list[float] = Field(default_factory=list)
    bid_absorption: float = 0.0
    liquidity_voids: list[float] = Field(default_factory=list)
    sweep_zones: list[float] = Field(default_factory=list)


class TradeSignal(BaseModel):
    symbol: Literal["NIFTY", "SENSEX"]
    direction: Literal["BUY", "SELL"]
    score: float
    rationale: list[str]
    confidence: float
    target_points: float = 5.0
    stop_points: float = 3.0
    ts: datetime = Field(default_factory=datetime.utcnow)


class RiskDecision(BaseModel):
    allowed: bool
    safe_mode: bool
    reasons: list[str] = Field(default_factory=list)
    max_qty: int = 0
    exposure_pct: float = 0.0
    adjusted_trailing_factor: float = 1.0


class OrderIntent(BaseModel):
    symbol: Literal["NIFTY", "SENSEX"]
    side: Literal["BUY", "SELL"]
    qty: int
    order_type: Literal["MARKET", "LIMIT", "IOC_LIMIT"]
    limit_price: float | None = None
    strategy_tag: str = "nexusquant-scalp"
    mode: Literal["simulator", "paper", "live"] = "simulator"


class Position(BaseModel):
    symbol: str
    qty: int
    avg_price: float
    ltp: float
    unrealized_pnl: float
    realized_pnl: float = 0.0


class TelemetrySnapshot(BaseModel):
    ts: datetime = Field(default_factory=datetime.utcnow)
    broker: BrokerState
    available_capital: float = 0.0
    used_margin: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    active_positions: list[Position] = Field(default_factory=list)
    open_orders: list[dict[str, Any]] = Field(default_factory=list)
    exposure_pct: float = 0.0
    mode: str = "simulator"
    stale_feed: bool = True
    tqs: float = 0.0
    signal: TradeSignal | None = None
    safe_mode_reason: str = ""
    heatmap: HeatmapSnapshot = Field(default_factory=HeatmapSnapshot)
    orderflow: OrderFlowSnapshot = Field(default_factory=OrderFlowSnapshot)

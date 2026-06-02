from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.container import AppContainer
from app.api.deps import get_container

router = APIRouter(prefix="/api/v1", tags=["nexusquant"])


class RiskConfigPayload(BaseModel):
    daily_capital: float = Field(gt=0)
    capital_allocation_pct: float = Field(gt=0, le=100)
    max_exposure_pct: float = Field(gt=0, le=100)
    ai_threshold: float = Field(ge=0, le=100)


class ManualTradePayload(BaseModel):
    symbol: str
    side: str
    qty: int = Field(gt=0)


@router.get("/state")
async def get_state(container: AppContainer = Depends(get_container)) -> dict:
    state = container.state
    settings = container.settings
    return {
        "mode": settings.trading_mode,
        "safe_mode": state.broker.safe_mode,
        "reason": state.broker.reason,
        "broker_connected": state.broker.broker_connected,
        "market_stream_connected": state.broker.market_stream_connected,
        "capital_available": state.capital_available,
        "used_margin": state.used_margin,
        "realized_pnl": state.realized_pnl,
        "unrealized_pnl": state.unrealized_pnl,
        "open_orders": state.open_orders,
        "active_positions": [p.model_dump() for p in state.active_positions],
    }


@router.post("/risk/config")
async def update_risk_config(
    payload: RiskConfigPayload,
    container: AppContainer = Depends(get_container),
) -> dict:
    container.settings.daily_capital = payload.daily_capital
    container.settings.capital_allocation_pct = payload.capital_allocation_pct
    container.settings.max_exposure_pct = payload.max_exposure_pct
    container.settings.ai_threshold = payload.ai_threshold
    return {"status": "ok", "message": "Risk configuration updated"}


@router.post("/trade/manual")
async def manual_trade(
    payload: ManualTradePayload,
    container: AppContainer = Depends(get_container),
) -> dict:
    if container.state.broker.safe_mode:
        raise HTTPException(status_code=423, detail="SAFE MODE active; manual trading disabled")
    return {
        "status": "accepted",
        "symbol": payload.symbol.upper(),
        "side": payload.side.upper(),
        "qty": payload.qty,
        "mode": container.settings.trading_mode,
    }

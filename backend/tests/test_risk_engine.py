from app.core.config import Settings
from app.core.schemas import BrokerState
from app.engines.risk_engine import RiskContext, RiskEngine


def test_risk_blocks_when_broker_disconnected() -> None:
    settings = Settings()
    engine = RiskEngine(settings)
    broker = BrokerState(broker_connected=False, market_stream_connected=False, safe_mode=True)
    ctx = RiskContext(
        available_capital=100000,
        used_margin=0,
        realized_pnl=0,
        unrealized_pnl=0,
        exposure_pct=0,
        slippage_bps=0,
        latency_ms=0,
        consecutive_losses=0,
        stale_feed=False,
    )

    decision = engine.evaluate(broker, ctx)
    assert not decision.allowed
    assert decision.safe_mode
    assert "Broker disconnected" in decision.reasons

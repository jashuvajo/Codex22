from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.state import RuntimeState
from app.engines.feature_engine import FeatureEngine
from app.engines.model_registry import ModelRegistry
from app.engines.training_engine import TrainingEngine
from app.services.market_data_collector import MarketDataCollector
from app.services.redis_bus import RedisBus
from app.services.scalping_orchestrator import ScalpingOrchestrator
from app.services.upstox_client import UpstoxClient
from app.services.ws_manager import WebSocketManager


@dataclass
class AppContainer:
    settings: Settings
    state: RuntimeState
    upstox: UpstoxClient
    ws_manager: WebSocketManager
    redis_bus: RedisBus
    feature_engine: FeatureEngine
    model_registry: ModelRegistry
    training_engine: TrainingEngine
    market_data_collector: MarketDataCollector
    orchestrator: ScalpingOrchestrator


def build_container() -> AppContainer:
    settings = get_settings()
    state = RuntimeState(capital_available=settings.daily_capital)
    upstox = UpstoxClient(settings)
    ws_manager = WebSocketManager()
    redis_bus = RedisBus(settings.redis_url)

    feature_engine = FeatureEngine()
    model_registry = ModelRegistry(settings)
    training_engine = TrainingEngine(settings, feature_engine, model_registry)
    market_data_collector = MarketDataCollector(feature_engine)

    orchestrator = ScalpingOrchestrator(
        settings,
        state,
        upstox,
        ws_manager,
        redis_bus,
        feature_engine,
        model_registry,
        training_engine,
        market_data_collector,
    )
    return AppContainer(
        settings=settings,
        state=state,
        upstox=upstox,
        ws_manager=ws_manager,
        redis_bus=redis_bus,
        feature_engine=feature_engine,
        model_registry=model_registry,
        training_engine=training_engine,
        market_data_collector=market_data_collector,
        orchestrator=orchestrator,
    )

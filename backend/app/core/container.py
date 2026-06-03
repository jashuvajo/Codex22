from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.state import RuntimeState
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
    orchestrator: ScalpingOrchestrator


def build_container() -> AppContainer:
    settings = get_settings()
    state = RuntimeState(capital_available=settings.daily_capital)
    upstox = UpstoxClient(settings)
    ws_manager = WebSocketManager()
    redis_bus = RedisBus(settings.redis_url)
    orchestrator = ScalpingOrchestrator(settings, state, upstox, ws_manager, redis_bus)
    return AppContainer(
        settings=settings,
        state=state,
        upstox=upstox,
        ws_manager=ws_manager,
        redis_bus=redis_bus,
        orchestrator=orchestrator,
    )

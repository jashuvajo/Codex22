from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes import router as api_router
from app.core.container import build_container
from app.core.db import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("nexusquant")


container = build_container()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    await container.redis_bus.connect()
    rest_ok = await container.upstox.connect()
    if not rest_ok:
        container.state.set_safe_mode(True, "Unable to connect to Upstox REST API")
        container.state.broker.broker_connected = False
        container.state.broker.market_stream_connected = False
    else:
        container.state.broker.broker_connected = True
    await container.orchestrator.start()
    try:
        yield
    finally:
        await container.orchestrator.stop()
        await container.upstox.close()
        await container.redis_bus.close()


app = FastAPI(
    title="NexusQuant Backend",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.state.container = container
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def healthcheck(request: Request) -> dict:
    app_container = request.app.state.container
    return {
        "status": "ok",
        "broker_connected": app_container.state.broker.broker_connected,
        "market_stream_connected": app_container.state.broker.market_stream_connected,
        "safe_mode": app_container.state.broker.safe_mode,
        "reason": app_container.state.broker.reason,
        "mode": app_container.settings.trading_mode,
    }


@app.get("/metrics")
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.websocket("/ws/telemetry")
async def telemetry_ws(websocket: WebSocket) -> None:
    app_container = websocket.app.state.container
    await app_container.ws_manager.connect(websocket)
    try:
        while True:
            # Keepalive; broadcast messages are pushed by orchestrator.
            await websocket.receive()
    except WebSocketDisconnect:
        await app_container.ws_manager.disconnect(websocket)

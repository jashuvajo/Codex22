from __future__ import annotations

import asyncio
import json
import logging
import random
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

import httpx
import websockets

from app.core.config import Settings
from app.core.schemas import MarketTick

logger = logging.getLogger(__name__)


class UpstoxClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._http: httpx.AsyncClient | None = None
        self._connected = False
        self._stream_connected = False
        self._market_ws: websockets.WebSocketClientProtocol | None = None
        self._latest_ticks: dict[str, MarketTick] = {}

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def stream_connected(self) -> bool:
        return self._stream_connected

    @property
    def latest_ticks(self) -> dict[str, MarketTick]:
        return self._latest_ticks

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.upstox_access_token}",
            "Accept": "application/json",
            "Api-Version": "2.0",
            "x-api-key": self.settings.upstox_api_key,
            # Cloudflare may block non-browser signatures; keep a stable browser UA.
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        }

    async def connect(self) -> bool:
        self._http = httpx.AsyncClient(timeout=6.0)
        if not self.settings.upstox_access_token:
            logger.warning("UPSTOX_ACCESS_TOKEN missing")
            self._connected = False
            return False
        try:
            profile_endpoint = f"{self.settings.upstox_base_url}{self.settings.upstox_profile_endpoint}"
            response = await self._http.get(profile_endpoint, headers=self._headers())
            response.raise_for_status()
            self._connected = True
            logger.info("Upstox REST connection established")
            return True
        except Exception as exc:
            self._connected = False
            logger.exception("Upstox REST connect failed: %s", exc)
            return False

    def _resolve_endpoint(self, endpoint: str) -> str:
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        base = self.settings.upstox_base_url.rstrip("/")
        if endpoint.startswith("/v3/") and base.endswith("/v2"):
            base = base[:-3]
        return f"{base}{endpoint}"

    async def _authorize_market_feed(self) -> str:
        if not self._http:
            raise RuntimeError("HTTP client is not initialized")
        endpoint = self._resolve_endpoint(self.settings.upstox_market_authorize_endpoint)
        response = await self._http.get(endpoint, headers=self._headers())
        response.raise_for_status()
        data = response.json()
        return data["data"]["authorized_redirect_uri"]

    async def market_stream(self) -> AsyncIterator[MarketTick]:
        """
        Upstox connectivity gate:
        until REST + market stream are both connected, yield nothing.
        """
        if not self._connected and not await self.connect():
            return

        try:
            ws_url = await self._authorize_market_feed()
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as ws:
                self._stream_connected = True
                self._market_ws = ws
                logger.info("MarketDataStreamerV3 websocket connected")

                subscribe_payload = {
                    "guid": f"nexusquant-{int(datetime.utcnow().timestamp())}",
                    "method": "sub",
                    "data": {
                        "mode": "full",
                        "instrumentKeys": [
                            self.settings.nifty_instrument_key,
                            self.settings.sensex_instrument_key,
                        ],
                    },
                }
                await ws.send(json.dumps(subscribe_payload))

                async for raw in ws:
                    tick = self._parse_tick(raw)
                    if not tick:
                        continue
                    self._latest_ticks[tick.symbol] = tick
                    yield tick
        except Exception as exc:
            self._stream_connected = False
            logger.exception("Market stream disconnected: %s", exc)
        finally:
            self._stream_connected = False
            self._market_ws = None

    def _parse_tick(self, raw: str) -> MarketTick | None:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None

        feeds = payload.get("data", {}).get("feeds", {})
        for instrument_key, content in feeds.items():
            ff = content.get("fullFeed", {})
            market_ff = ff.get("marketFF", {})
            ltp = market_ff.get("ltpc", {}).get("ltp")
            if ltp is None:
                continue
            bid_ask = market_ff.get("marketLevel", {}).get("bidAskQuote", [{}])
            quote = bid_ask[0] if bid_ask else {}
            vwap = market_ff.get("eFeedDetails", {}).get("vwap", ltp)
            volume = market_ff.get("eFeedDetails", {}).get("vtt", 0.0)
            symbol = "NIFTY" if "Nifty" in instrument_key or "NIFTY" in instrument_key else "SENSEX"
            return MarketTick(
                symbol=symbol,  # type: ignore[arg-type]
                instrument_key=instrument_key,
                ltp=float(ltp),
                volume=float(volume),
                bid=float(quote.get("bp", ltp)),
                ask=float(quote.get("ap", ltp)),
                vwap=float(vwap),
                delta=float(random.uniform(-1, 1)),
            )
        return None

    async def get_funds(self) -> dict[str, Any]:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=6.0)
        endpoint = f"{self.settings.upstox_base_url}/user/get-funds-and-margin"
        response = await self._http.get(endpoint, headers=self._headers())
        response.raise_for_status()
        return response.json()

    async def get_positions(self) -> dict[str, Any]:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=6.0)
        endpoint = f"{self.settings.upstox_base_url}/portfolio/short-term-positions"
        response = await self._http.get(endpoint, headers=self._headers())
        response.raise_for_status()
        return response.json()

    async def get_orders(self) -> dict[str, Any]:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=6.0)
        endpoint = f"{self.settings.upstox_base_url}/order/retrieve-all"
        response = await self._http.get(endpoint, headers=self._headers())
        response.raise_for_status()
        return response.json()

    async def place_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=6.0)
        endpoint = f"{self.settings.upstox_base_url}/order/place"
        response = await self._http.post(endpoint, headers=self._headers(), json=payload)
        response.raise_for_status()
        return response.json()

    async def option_chain(self, symbol: str, expiry_date: str) -> dict[str, Any]:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=6.0)
        endpoint = f"{self.settings.upstox_base_url}/option/chain"
        params = {"instrument_key": symbol, "expiry_date": expiry_date}
        response = await self._http.get(endpoint, headers=self._headers(), params=params)
        response.raise_for_status()
        return response.json()

    async def simulator_stream(self) -> AsyncIterator[MarketTick]:
        """
        Local dev helper. Not used for production gating when REQUIRE_LIVE_UPSTOX_CONNECTION=true.
        """
        base_nifty = 23500.0
        base_sensex = 78000.0
        self._stream_connected = True
        while True:
            base_nifty += random.uniform(-7, 9)
            base_sensex += random.uniform(-22, 27)
            for symbol, ltp, key in (
                ("NIFTY", base_nifty, self.settings.nifty_instrument_key),
                ("SENSEX", base_sensex, self.settings.sensex_instrument_key),
            ):
                spread = max(ltp * 0.0005, 0.05)
                tick = MarketTick(
                    symbol=symbol,  # type: ignore[arg-type]
                    instrument_key=key,
                    ltp=round(ltp, 2),
                    bid=round(ltp - spread, 2),
                    ask=round(ltp + spread, 2),
                    vwap=round(ltp - random.uniform(-1.5, 1.5), 2),
                    volume=random.randint(10000, 300000),
                    delta=random.uniform(-0.5, 0.9),
                )
                self._latest_ticks[symbol] = tick
                yield tick
            await asyncio.sleep(1)

    async def close(self) -> None:
        self._stream_connected = False
        if self._market_ws:
            await self._market_ws.close()
        if self._http:
            await self._http.aclose()

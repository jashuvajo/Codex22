from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisBus:
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self.redis: Redis | None = None
        self.online = False

    async def connect(self) -> None:
        try:
            self.redis = Redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            self.online = True
            logger.info("Redis connected")
        except Exception as exc:
            self.online = False
            logger.warning("Redis unavailable: %s", exc)

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        if not self.redis or not self.online:
            return
        await self.redis.publish(channel, json.dumps(payload))

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()

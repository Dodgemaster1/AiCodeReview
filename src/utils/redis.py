import asyncio
import hashlib
import json
import logging
import os
from aiocache import RedisCache
from .read_config import get_redis_config

log = logging.getLogger('uvicorn.error')


class Redis:
    def __init__(self) -> None:
        config_host, config_port = get_redis_config()
        self.host: str = os.getenv('REDIS_HOST', config_host)
        self.port: int = int(os.getenv('REDIS_PORT', config_port))
        self.is_valid = True

        try:
            self.cache: RedisCache = RedisCache(endpoint=self.host, port=self.port)
            log.info("Connected to Redis")
        except Exception as e:
            log.error(f"Error connecting to Redis: {e}")
            self.is_valid = False

    async def get(self, key: str, prefix: str = '') -> bytes | None:
        if not self.is_valid:
            return None
        return await self.cache.get(key, namespace=prefix)

    async def set(self, key: str, value: str, time: int = 300, prefix: str = '') -> None:
        if not self.is_valid:
            return
        asyncio.create_task(self.cache.set(key, value, ttl=time, namespace=prefix))

    @staticmethod
    def hash_args(*args, **kwargs) -> str:
        return hashlib.sha256(json.dumps([args, kwargs]).encode()).hexdigest()

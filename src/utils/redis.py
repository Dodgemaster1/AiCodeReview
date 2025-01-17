import hashlib
import json
import logging
import os
from typing import Any
from redis import Redis, exceptions
from .read_config import get_redis_config, ConfigError

log = logging.getLogger('uvicorn.error')

class RedisCache:
    def __init__(self):
        self.host: str
        self.port: int
        config_host, config_port = get_redis_config()
        self.host: str = os.getenv('REDIS_HOST', config_host)
        self.port: int = int(os.getenv('REDIS_PORT', config_port))
        if self.host is None or self.port is None:
            raise ConfigError("Redis host and port must be set in config.json")
        self.cache: Redis | None = None

        try:
            self.cache: Redis = Redis(host=self.host, port=self.port)
            self.cache.ping()
            log.info("Connected to Redis")
        except exceptions.ConnectionError as e:
            log.error(f"Error connecting to Redis: {e}")

    def get(self, key: str, prefix: str = '') -> Any:
        if self.cache is None:
            return None
        full_key: str = f"{prefix}:{key}"
        return self.cache.get(full_key)

    def set(self, key: str, value: Any, time: int, prefix: str = '') -> None:
        if self.cache is None:
            return
        full_key: str = f"{prefix}:{key}"
        self.cache.set(full_key, value, ex=time)

    @staticmethod
    def hash_args(*args, **kwargs) -> str:
        return hashlib.sha256(json.dumps([args, kwargs]).encode()).hexdigest()

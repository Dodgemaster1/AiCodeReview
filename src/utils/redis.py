import hashlib
import json
import logging
import os
from redis import Redis, exceptions
from .read_config import get_redis_config

log = logging.getLogger('uvicorn.error')

class RedisCache:
    def __init__(self) -> None:
        config_host, config_port = get_redis_config()
        self.host: str = os.getenv('REDIS_HOST', config_host)
        self.port: int = int(os.getenv('REDIS_PORT', config_port))

        try:
            self.cache: Redis | None = Redis(host=self.host, port=self.port)
            self.cache.ping()
            log.info("Connected to Redis")
        except exceptions.ConnectionError as e:
            log.error(f"Error connecting to Redis: {e}")
            self.cache = None

    def get(self, key: str, prefix: str = '') -> bytes | None:
        if self.cache is None:
            return None
        full_key: str = f"{prefix}:{key}"
        return self.cache.get(full_key)

    def set(self, key: str, value: str, time: int, prefix: str = '') -> None:
        if self.cache is None:
            return
        full_key: str = f"{prefix}:{key}"
        self.cache.set(full_key, value, ex=time)

    @staticmethod
    def hash_args(*args, **kwargs) -> str:
        return hashlib.sha256(json.dumps([args, kwargs]).encode()).hexdigest()

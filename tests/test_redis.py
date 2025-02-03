import asyncio
from src.utils.redis import Redis
import pytest


@pytest.mark.asyncio
async def test_redis():
    redis = Redis()
    await redis.set("test_key", "test_value", 10)
    await asyncio.sleep(0.1)
    assert await redis.get("test_key") == "test_value"

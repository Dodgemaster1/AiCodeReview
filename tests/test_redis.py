from src.utils.redis import RedisCache


def test_redis():
    redis = RedisCache()
    redis.set("test_key", "test_value", 10)
    assert redis.get("test_key") == b"test_value"

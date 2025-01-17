import json
from pathlib import Path

CONFIG_PATH: Path = Path(__file__).resolve().parent.parent.parent / "config.json"

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        return config

def get_gemini_api_key() -> str | None:
    config = load_config()
    return config.get('api', {}).get("gemini_api_key")

def get_github_token() -> str | None:
    config = load_config()
    return config.get('api', {}).get("github_token")

def get_redis_config() -> tuple[str, int] | tuple[None, None]:
    config = load_config()
    return config.get("redis", {}).get("host", "localhost"), config.get("redis", {}).get("port", 6379)


class ConfigError(Exception):
    pass

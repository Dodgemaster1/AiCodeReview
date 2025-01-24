import json
from pathlib import Path
from typing import Final

CONFIG_PATH: Final[Path] = Path(__file__).resolve().parent.parent.parent / "config.json"

def load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        return config

def get_gemini_api_key() -> str:
    config = load_config()
    try:
        return config['api']["gemini_api_key"]
    except KeyError:
        raise ConfigError("Gemini api key must be set in config.json")

def get_github_token() -> str:
    config = load_config()
    try:
        return config['api']["github_token"]
    except KeyError:
        raise ConfigError("Github token must be set in config.json")

def get_redis_config() -> tuple[str, int]:
    config = load_config()
    return config.get("redis", {}).get("host", "localhost"), config.get("redis", {}).get("port", 6379)



class ConfigError(Exception):
    pass

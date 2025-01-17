from src.utils.read_config import load_config, get_github_token, get_gemini_api_key

def test_load_config():
    config = load_config()
    assert config is not None

def test_get_github_token():
    token = get_github_token()
    assert token is not None

def test_get_gemini_api_key():
    token = get_gemini_api_key()
    assert token is not None


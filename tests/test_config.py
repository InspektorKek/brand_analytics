import os
from config import load_env_config


def test_load_env_config_multiple_chat_ids(monkeypatch):
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123, 456")
    env = load_env_config()
    assert env.telegram_chat_ids == ["123", "456"]

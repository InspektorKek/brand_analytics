import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Any

import requests
from dotenv import load_dotenv

from config import load_env_config
from orchestrator import run_orchestration
from utils import escape_markdown_v2, split_message

BASE_URL = "https://api.telegram.org"
LOG_PATH = "logs/telegram_bot.log"


def setup_logging() -> None:
    logger = logging.getLogger()
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_updates(bot_token: str, offset: int | None) -> dict[str, Any]:
    url = f"{BASE_URL}/bot{bot_token}/getUpdates"
    params: dict[str, Any] = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(url, params=params, timeout=35)
    resp.raise_for_status()
    return resp.json()


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    url = f"{BASE_URL}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def handle_text(env, message: dict) -> None:
    logger = logging.getLogger(__name__)
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return

    if env.telegram_chat_ids and str(chat_id) not in set(env.telegram_chat_ids):
        return

    if not text:
        return

    logger.info("Handling message chat_id=%s text=%s", chat_id, text[:200])
    try:
        response = run_orchestration(
            user_message=text,
            openrouter_api_key=env.openrouter_api_key,
            instagram_access_token=env.instagram_access_token,
            instagram_user_id=env.instagram_user_id,
            pinterest_access_token=env.pinterest_access_token,
            apify_token=env.apify_token,
        )
    except Exception:
        logger.exception("Orchestration failed")
        response = "Maaf, terjadi error saat mengambil data. Coba lagi nanti."

    safe = escape_markdown_v2(response)
    for part in split_message(safe):
        send_message(env.telegram_bot_token, chat_id, part)
    logger.info("Sent response chat_id=%s parts=%s", chat_id, len(split_message(safe)))


def run_bot() -> None:
    load_dotenv()
    setup_logging()
    logger = logging.getLogger(__name__)
    env = load_env_config()

    if not env.telegram_bot_token:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN")
    if not env.openrouter_api_key:
        raise SystemExit("Missing OPENROUTER_API_KEY")
    if not env.instagram_access_token or not env.instagram_user_id:
        raise SystemExit("Missing INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_USER_ID")

    logger.info("Telegram bot started in long-polling mode")
    offset = None
    while True:
        try:
            data = get_updates(env.telegram_bot_token, offset)
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                if "text" in message:
                    handle_text(env, message)
        except requests.RequestException:
            logger.exception("Telegram API request failed")
            time.sleep(5)
        except Exception:
            logger.exception("Unhandled error in bot loop")
            time.sleep(2)


if __name__ == "__main__":
    run_bot()

import os
import threading
import logging
from logging.handlers import RotatingFileHandler
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request

from config import load_env_config
from orchestrator import run_orchestration
from utils import escape_markdown_v2, split_message
import requests

load_dotenv()

app = FastAPI()
LOG_PATH = "logs/telegram_webhook.log"


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


def send_message(bot_token: str, chat_id: int, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def handle_update(env, update: dict) -> None:
    logger = logging.getLogger(__name__)
    message = update.get("message") or update.get("edited_message") or {}
    text = message.get("text", "").strip()
    chat_id = message.get("chat", {}).get("id")
    if not chat_id or not text:
        return

    if env.telegram_chat_ids and str(chat_id) not in set(env.telegram_chat_ids):
        return

    logger.info("Handling webhook message chat_id=%s text=%s", chat_id, text[:200])
    response = run_orchestration(
        user_message=text,
        openrouter_api_key=env.openrouter_api_key,
        instagram_access_token=env.instagram_access_token,
        instagram_user_id=env.instagram_user_id,
        pinterest_access_token=env.pinterest_access_token,
        apify_token=env.apify_token,
    )

    safe = escape_markdown_v2(response)
    for part in split_message(safe):
        send_message(env.telegram_bot_token, chat_id, part)
    logger.info("Sent response chat_id=%s parts=%s", chat_id, len(split_message(safe)))


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, Any]:
    setup_logging()
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if secret and x_telegram_bot_api_secret_token != secret:
        raise HTTPException(status_code=401, detail="Invalid secret token")

    update = await request.json()

    env = load_env_config()
    if not env.telegram_bot_token:
        raise HTTPException(status_code=500, detail="Missing TELEGRAM_BOT_TOKEN")

    thread = threading.Thread(target=handle_update, args=(env, update), daemon=True)
    thread.start()

    return {"ok": True}


def set_webhook() -> None:
    load_dotenv()
    env = load_env_config()
    if not env.telegram_bot_token:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "")
    secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not webhook_url:
        raise SystemExit("Missing TELEGRAM_WEBHOOK_URL")

    url = f"https://api.telegram.org/bot{env.telegram_bot_token}/setWebhook"
    payload = {"url": webhook_url}
    if secret:
        payload["secret_token"] = secret
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    print(resp.json())


if __name__ == "__main__":
    load_dotenv()
    print("Run with: uvicorn telegram_webhook:app --host 0.0.0.0 --port 8000")

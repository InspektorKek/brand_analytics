import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime

TIMEZONE = ZoneInfo("Asia/Jakarta")

DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-chat"
FALLBACK_OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"

PINTEREST_REGION = os.getenv("PINTEREST_REGION", "ID")
INSTAGRAM_ACCOUNT_COUNTRY = os.getenv("INSTAGRAM_ACCOUNT_COUNTRY", "ID")
USE_MCP = os.getenv("USE_MCP", "true").lower() == "true"
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v19.0")

APIFY_DATASET_ID = os.getenv("APIFY_DATASET_ID", "")
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID", "")
APIFY_TASK_ID = os.getenv("APIFY_TASK_ID", "")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

TRACKED_HASHTAGS = [
    "ootd",
    "outfitoftheday",
    "fashionblogger",
    "streetstyle",
    "fashionindonesia",
    "ootdindonesia",
    "hijabfashion",
    "sustainablefashion",
]

COMPETITOR_ACCOUNTS = [
    # Add Instagram usernames here (business/creator accounts)
    # "examplebrand",
]

FALLBACK_TRENDS = [
    {
        "keyword": "modest layering", 
        "volume": None,
        "volume_change": None,
        "demographics": {},
        "prediction": {"direction": "up", "confidence": 0.6},
        "source": "fallback"
    },
    {
        "keyword": "linen set", 
        "volume": None,
        "volume_change": None,
        "demographics": {},
        "prediction": {"direction": "up", "confidence": 0.55},
        "source": "fallback"
    },
    {
        "keyword": "neutral palette", 
        "volume": None,
        "volume_change": None,
        "demographics": {},
        "prediction": {"direction": "stable", "confidence": 0.5},
        "source": "fallback"
    },
]


@dataclass
class EnvConfig:
    openrouter_api_key: str
    instagram_access_token: str
    instagram_user_id: str
    telegram_bot_token: str
    telegram_chat_ids: list[str]
    pinterest_access_token: str | None
    apify_token: str | None


def now_wib() -> datetime:
    return datetime.now(TIMEZONE)


def load_env_config() -> EnvConfig:
    raw_chat_ids = os.getenv("TELEGRAM_CHAT_ID", "")
    chat_ids = [cid.strip() for cid in raw_chat_ids.split(",") if cid.strip()]
    return EnvConfig(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        instagram_access_token=os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        instagram_user_id=os.getenv("INSTAGRAM_USER_ID", ""),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_ids=chat_ids,
        pinterest_access_token=os.getenv("PINTEREST_ACCESS_TOKEN"),
        apify_token=os.getenv("APIFY_TOKEN"),
    )

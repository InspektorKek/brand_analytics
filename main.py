import json
import time
from typing import Any

from dotenv import load_dotenv
import requests

from config import (
    TRACKED_HASHTAGS,
    COMPETITOR_ACCOUNTS,
    FALLBACK_TRENDS,
    DEFAULT_OPENROUTER_MODEL,
    FALLBACK_OPENROUTER_MODEL,
    PINTEREST_REGION,
    now_wib,
    load_env_config,
)
from instagram_api import InstagramClient
from pinterest_api import PinterestClient
from openrouter_ai import OpenRouterClient
from utils import summarize_media_items, summarize_user_media, escape_markdown_v2, split_message
from prompting import (
    SYSTEM_PROMPT,
    build_strategy_prompt,
    build_repair_prompt,
    validate_result,
    format_report,
)


def telegram_send(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()


def fetch_pinterest_trends(pinterest: PinterestClient) -> dict:
    combined: list[dict] = []
    for trend_type in ["growing", "monthly"]:
        data = pinterest.get_trends_keywords(region=PINTEREST_REGION, trend_type=trend_type)
        for trend in data.get("trends", []):
            trend["trend_type"] = trend_type
        combined.extend(data.get("trends", []))
    return {"trends": combined, "source": "pinterest_api"}


def summarize_competitor(raw: dict, username: str) -> dict[str, Any]:
    business = raw.get("business_discovery", raw)
    media_items = business.get("media", {}).get("data", []) if isinstance(business, dict) else []
    return {
        "username": business.get("username", username) if isinstance(business, dict) else username,
        "followers_count": business.get("followers_count") if isinstance(business, dict) else None,
        "media_count": business.get("media_count") if isinstance(business, dict) else None,
        "media_summary": summarize_media_items(media_items, top_n_keywords=6),
    }


def main() -> None:
    load_dotenv()
    env = load_env_config()

    if not env.telegram_bot_token or not env.telegram_chat_id:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

    if not env.openrouter_api_key:
        raise SystemExit("Missing OPENROUTER_API_KEY")

    pinterest_trends: dict = {"trends": FALLBACK_TRENDS, "source": "fallback"}
    if env.pinterest_access_token:
        try:
            pinterest = PinterestClient(env.pinterest_access_token)
            pinterest_trends = fetch_pinterest_trends(pinterest)
        except Exception as exc:
            pinterest_trends = {"trends": FALLBACK_TRENDS, "source": f"fallback: {exc}"}

    hashtag_data = []
    user_stats = {"note": "Instagram data not available"}
    competitor_data = []

    if env.instagram_access_token and env.instagram_user_id:
        try:
            instagram = InstagramClient(env.instagram_access_token)
            media = instagram.get_user_media(env.instagram_user_id)
            user_stats = summarize_user_media(media)

            hashtags = TRACKED_HASHTAGS[:6]
            for tag in hashtags:
                result = instagram.hashtag_search(tag, env.instagram_user_id)
                data = result.get("data", [])
                if not data:
                    hashtag_data.append({"hashtag": tag, "note": "not found"})
                    continue
                hashtag_id = data[0].get("id")
                top_media = instagram.hashtag_top_media(hashtag_id, env.instagram_user_id)
                recent_media = instagram.hashtag_recent_media(hashtag_id, env.instagram_user_id)
                hashtag_data.append(
                    {
                        "hashtag": tag,
                        "top_summary": summarize_media_items(top_media.get("data", [])[:20]),
                        "recent_summary": summarize_media_items(recent_media.get("data", [])[:20]),
                    }
                )
                time.sleep(1)

            for username in COMPETITOR_ACCOUNTS:
                try:
                    competitor = instagram.business_discovery(env.instagram_user_id, username)
                    competitor_data.append(summarize_competitor(competitor, username))
                except Exception as exc:
                    competitor_data.append({"username": username, "error": str(exc)})
        except Exception as exc:
            user_stats = {"note": f"Instagram error: {exc}"}

    prompt = build_strategy_prompt(
        user_request="Daily trend report",
        profile={},
        user_stats=user_stats,
        hashtag_data=hashtag_data,
        pinterest_trends=pinterest_trends,
        apify_trends={},
        competitor_data=competitor_data,
    )

    ai = OpenRouterClient(env.openrouter_api_key)
    try:
        analysis = ai.analyze_trends(prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
    except Exception:
        try:
            analysis = ai.analyze_trends(prompt, model=FALLBACK_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
        except Exception as exc:
            error_text = f"Trend analysis failed: {exc}"
            telegram_send(env.telegram_bot_token, env.telegram_chat_id, escape_markdown_v2(error_text))
            raise

    now = now_wib()
    header = (
        "DAILY TREND REPORT\n"
        f"Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Time: {now.strftime('%H:%M')} WIB\n\n"
    )

    parsed = None
    try:
        parsed = json.loads(analysis)
        if isinstance(parsed, dict):
            validate_result(parsed)
            body = format_report(parsed)
        else:
            body = analysis
    except (json.JSONDecodeError, ValueError):
        repair_prompt = build_repair_prompt(analysis)
        try:
            repaired = ai.analyze_trends(repair_prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
            parsed = json.loads(repaired)
            if isinstance(parsed, dict):
                validate_result(parsed)
                body = format_report(parsed)
            else:
                body = analysis
        except Exception:
            body = analysis

    message = header + body
    safe_message = escape_markdown_v2(message)

    for part in split_message(safe_message):
        telegram_send(env.telegram_bot_token, env.telegram_chat_id, part)


if __name__ == "__main__":
    main()

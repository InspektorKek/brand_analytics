from typing import Any
import time

from config import PINTEREST_REGION, TRACKED_HASHTAGS
from instagram_api import InstagramClient
from pinterest_api import PinterestClient
from apify_client import ApifyClient
from utils import summarize_media_items, extract_keywords


class LocalMCP:
    """
    Local MCP-style tool adapter.

    This adapter keeps a narrow, auditable tool surface and can be
    swapped later for real MCP server calls (ig-mcp, google-news-trends-mcp, etc.).
    """

    def __init__(self, instagram: InstagramClient | None, pinterest: PinterestClient | None, apify: ApifyClient | None):
        self.instagram = instagram
        self.pinterest = pinterest
        self.apify = apify

    def tool_instagram_profile(self, user_id: str) -> dict[str, Any]:
        if not self.instagram:
            return {"note": "Instagram client not configured"}
        try:
            return self.instagram.get_user_profile(user_id)
        except Exception as exc:
            return {"note": "Instagram profile error", "error": str(exc)}

    def tool_instagram_hashtags(self, user_id: str, limit: int = 6) -> list[dict[str, Any]]:
        if not self.instagram:
            return []
        results = []
        for tag in TRACKED_HASHTAGS[:limit]:
            try:
                search = self.instagram.hashtag_search(tag, user_id)
                data = search.get("data", [])
                if not data:
                    results.append({"hashtag": tag, "note": "not found"})
                    continue
                hashtag_id = data[0].get("id")
                top_media = self.instagram.hashtag_top_media(hashtag_id, user_id)
                recent_media = self.instagram.hashtag_recent_media(hashtag_id, user_id)
                results.append(
                    {
                        "hashtag": tag,
                        "top_summary": summarize_media_items(top_media.get("data", [])[:20]),
                        "recent_summary": summarize_media_items(recent_media.get("data", [])[:20]),
                    }
                )
            except Exception as exc:
                results.append({"hashtag": tag, "note": "hashtag error", "error": str(exc)})
            time.sleep(1)
        return results

    def tool_pinterest_trends(self) -> dict[str, Any]:
        if not self.pinterest:
            return {"trends": [], "note": "Pinterest client not configured"}
        try:
            combined = []
            for trend_type in ["growing", "monthly"]:
                data = self.pinterest.get_trends_keywords(region=PINTEREST_REGION, trend_type=trend_type)
                for trend in data.get("trends", []):
                    trend["trend_type"] = trend_type
                combined.extend(data.get("trends", []))
            return {"trends": combined, "source": "pinterest_api"}
        except Exception as exc:
            return {"trends": [], "note": "Pinterest error", "error": str(exc)}

    def tool_apify_trends(self, dataset_id: str, limit: int = 20) -> dict[str, Any]:
        if not self.apify:
            return {"items": [], "note": "Apify client not configured"}
        items = self.apify.get_dataset_items(dataset_id, limit=limit)
        captions = [str(item.get("caption", "")) for item in items if isinstance(item, dict)]
        keywords = extract_keywords(captions, top_n=10)
        return {"items": items, "top_keywords": keywords}

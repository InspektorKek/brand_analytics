import requests

from config import GRAPH_API_VERSION

BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class InstagramClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def _get(self, path: str, params: dict) -> dict:
        url = f"{BASE_URL}{path}"
        params = {**params, "access_token": self.access_token}
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_user_media(self, user_id: str, limit: int = 30) -> dict:
        fields = (
            "id,caption,media_type,timestamp,like_count,comments_count,"
            "insights.metric(impressions,reach,saved,shares)"
        )
        return self._get(f"/{user_id}/media", {"fields": fields, "limit": limit})

    def get_user_profile(self, user_id: str) -> dict:
        fields = "username,biography,followers_count,media_count"
        return self._get(f"/{user_id}", {"fields": fields})

    def hashtag_search(self, hashtag: str, user_id: str) -> dict:
        return self._get("/ig_hashtag_search", {"q": hashtag, "user_id": user_id})

    def hashtag_top_media(self, hashtag_id: str, user_id: str, limit: int = 15) -> dict:
        fields = "id,caption,media_type,media_url,permalink,like_count,comments_count,timestamp"
        return self._get(f"/{hashtag_id}/top_media", {"user_id": user_id, "fields": fields, "limit": limit})

    def hashtag_recent_media(self, hashtag_id: str, user_id: str, limit: int = 15) -> dict:
        fields = "id,caption,media_type,media_url,permalink,like_count,comments_count,timestamp"
        return self._get(f"/{hashtag_id}/recent_media", {"user_id": user_id, "fields": fields, "limit": limit})

    def business_discovery(self, user_id: str, username: str) -> dict:
        fields = (
            f"business_discovery.username({username})"
            "{followers_count,media_count,media"
            "{caption,like_count,comments_count,media_type,permalink,timestamp}}"
        )
        return self._get(f"/{user_id}", {"fields": fields})

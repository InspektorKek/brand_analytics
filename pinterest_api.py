import requests

BASE_URL = "https://api.pinterest.com/v5"


class PinterestClient:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def _get(self, path: str, params: dict) -> dict:
        url = f"{BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_trends_keywords(
        self,
        region: str,
        trend_type: str = "growing",
        interests: str = "womens_fashion,mens_fashion,beauty",
        include_demographics: bool = True,
        include_prediction: bool = True,
        limit: int = 20,
    ) -> dict:
        path = f"/trends/keywords/{region}/top/{trend_type}"
        params = {
            "interests": interests,
            "include_demographics": str(include_demographics).lower(),
            "include_prediction": str(include_prediction).lower(),
            "limit": limit,
        }
        return self._get(path, params)

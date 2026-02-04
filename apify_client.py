import requests

BASE_URL = "https://api.apify.com/v2"


class ApifyClient:
    def __init__(self, token: str):
        self.token = token

    def get_dataset_items(self, dataset_id: str, limit: int = 20) -> list[dict]:
        if not dataset_id:
            return []
        url = f"{BASE_URL}/datasets/{dataset_id}/items"
        params = {"clean": "true", "limit": limit, "token": self.token}
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return []

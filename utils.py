import re
from collections import Counter
from typing import Any

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "you", "your", "are", "but", "not",
    "have", "has", "had", "was", "were", "from", "they", "their", "our", "out", "about",
    "into", "what", "when", "where", "why", "how", "its", "it's", "a", "an", "to", "of",
    "in", "on", "at", "by", "as", "or", "if", "is", "be", "been", "we", "us", "me", "my",
    "yang", "dan", "untuk", "dengan", "ini", "itu", "kamu", "kalian", "kami", "kita",
    "mereka", "dari", "ke", "di", "pada", "oleh", "sebagai", "atau", "jika", "adalah",
    "sudah", "belum", "akan", "bisa", "dapat", "lagi", "juga", "lebih", "kurang",
    "baru", "lama", "saja", "aja", "nih", "yah", "ya", "nggak", "tidak",
}


def median(values: list[int | float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    mid = len(values) // 2
    if len(values) % 2 == 1:
        return float(values[mid])
    return (values[mid - 1] + values[mid]) / 2


def extract_keywords(captions: list[str], top_n: int = 10) -> list[str]:
    counter: Counter[str] = Counter()
    for caption in captions:
        for token in re.findall(r"[A-Za-z0-9#@]+", caption.lower()):
            token = token.lstrip("#")
            if len(token) < 3:
                continue
            if token in STOPWORDS:
                continue
            counter[token] += 1
    return [word for word, _ in counter.most_common(top_n)]


def summarize_media_items(items: list[dict], top_n_keywords: int = 8) -> dict[str, Any]:
    likes = []
    comments = []
    captions = []
    media_type_counts: dict[str, int] = {}
    for item in items:
        likes_val = item.get("like_count")
        comments_val = item.get("comments_count")
        if isinstance(likes_val, int):
            likes.append(likes_val)
        if isinstance(comments_val, int):
            comments.append(comments_val)
        caption = item.get("caption")
        if isinstance(caption, str):
            captions.append(caption)
        media_type = item.get("media_type")
        if media_type:
            media_type_counts[media_type] = media_type_counts.get(media_type, 0) + 1

    return {
        "count": len(items),
        "median_likes": median(likes),
        "median_comments": median(comments),
        "media_type_counts": media_type_counts,
        "top_keywords": extract_keywords(captions, top_n=top_n_keywords),
    }


def summarize_user_media(media: dict) -> dict[str, Any]:
    items = media.get("data", [])
    if not items:
        return {"count": 0, "note": "No media returned"}

    total_likes = 0
    total_comments = 0
    total_impressions = 0
    total_reach = 0
    recent = []
    captions = []
    media_type_counts: dict[str, int] = {}

    for item in items:
        total_likes += item.get("like_count", 0) or 0
        total_comments += item.get("comments_count", 0) or 0
        insights = item.get("insights", {}).get("data", [])
        metrics = {m.get("name"): m.get("values", [{}])[0].get("value", 0) for m in insights}
        total_impressions += metrics.get("impressions", 0) or 0
        total_reach += metrics.get("reach", 0) or 0
        caption = item.get("caption")
        if isinstance(caption, str):
            captions.append(caption)
        media_type = item.get("media_type")
        if media_type:
            media_type_counts[media_type] = media_type_counts.get(media_type, 0) + 1
        recent.append(
            {
                "id": item.get("id"),
                "media_type": item.get("media_type"),
                "timestamp": item.get("timestamp"),
                "like_count": item.get("like_count"),
                "comments_count": item.get("comments_count"),
            }
        )

    denom = total_impressions or total_reach or 1
    engagement_rate = (total_likes + total_comments) / denom

    top_posts = sorted(
        items,
        key=lambda x: (x.get("like_count") or 0) + (x.get("comments_count") or 0),
        reverse=True,
    )[:3]

    return {
        "count": len(items),
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_impressions": total_impressions,
        "total_reach": total_reach,
        "engagement_rate": round(engagement_rate, 4),
        "recent": recent[:5],
        "top_keywords": extract_keywords(captions, top_n=10),
        "media_type_counts": media_type_counts,
        "top_posts": [
            {
                "id": post.get("id"),
                "media_type": post.get("media_type"),
                "like_count": post.get("like_count"),
                "comments_count": post.get("comments_count"),
                "timestamp": post.get("timestamp"),
            }
            for post in top_posts
        ],
    }


def escape_markdown_v2(text: str) -> str:
    replacements = [
        ("\\", "\\\\"),
        ("_", "\\_"),
        ("*", "\\*"),
        ("[", "\\["),
        ("]", "\\]"),
        ("(", "\\("),
        (")", "\\)"),
        ("~", "\\~"),
        ("`", "\\`"),
        (">", "\\>"),
        ("#", "\\#"),
        ("+", "\\+"),
        ("-", "\\-"),
        ("=", "\\="),
        ("|", "\\|"),
        ("{", "\\{"),
        ("}", "\\}"),
        (".", "\\."),
        ("!", "\\!"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def split_message(text: str, max_len: int = 3500) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    current = []
    current_len = 0
    for paragraph in text.split("\n\n"):
        if len(paragraph) > max_len:
            if current:
                parts.append("\n\n".join(current))
                current = []
                current_len = 0
            for i in range(0, len(paragraph), max_len):
                parts.append(paragraph[i : i + max_len])
            continue
        if current_len + len(paragraph) + 2 > max_len and current:
            parts.append("\n\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += len(paragraph) + 2
    if current:
        parts.append("\n\n".join(current))
    return parts

from utils import escape_markdown_v2, split_message, extract_keywords, summarize_media_items


def test_escape_markdown_v2():
    text = "Hello *world* [link](x)!"
    escaped = escape_markdown_v2(text)
    assert "\\*" in escaped
    assert "\\[" in escaped
    assert "\\]" in escaped


def test_split_message():
    text = "a" * 4000
    parts = split_message(text, max_len=3500)
    assert len(parts) == 2
    assert sum(len(p) for p in parts) >= 4000


def test_extract_keywords():
    captions = ["Hello world #fashion", "Fashion trends in Indonesia"]
    keywords = extract_keywords(captions, top_n=5)
    assert "fashion" in keywords


def test_summarize_media_items():
    items = [
        {"like_count": 10, "comments_count": 2, "caption": "Test one", "media_type": "IMAGE"},
        {"like_count": 20, "comments_count": 4, "caption": "Test two", "media_type": "REEL"},
    ]
    summary = summarize_media_items(items)
    assert summary["count"] == 2
    assert summary["median_likes"] == 15
    assert "IMAGE" in summary["media_type_counts"]

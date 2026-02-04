import json
from typing import Any

SYSTEM_PROMPT = (
    "You are TrendAnalyst, an expert fashion/lifestyle content strategist for Indonesia. "
    "Respond in bilingual format (Bahasa Indonesia and English). Be specific, actionable, "
    "data-driven, and prioritize clarity. Do not invent data. Use only the provided data."
)


def build_strategy_prompt(
    user_request: str,
    profile: dict[str, Any],
    user_stats: dict[str, Any],
    hashtag_data: list[dict[str, Any]],
    pinterest_trends: dict[str, Any],
    apify_trends: dict[str, Any],
    competitor_data: list[dict[str, Any]],
) -> str:
    output_schema = {
        "top_trends": [
            {
                "name_id": "string",
                "name_en": "string",
                "platform": "Instagram | Pinterest | Both",
                "urgency_score": 1,
                "urgency_label_id": "string",
                "urgency_label_en": "string",
                "fit_score": 1,
                "evidence": [{"source": "string", "metric": "string", "value": "string"}],
                "content_angle_id": "string",
                "content_angle_en": "string",
            }
        ],
        "content_ideas": [
            {
                "title_id": "string",
                "title_en": "string",
                "platform": "string",
                "hook_id": "string",
                "hook_en": "string",
                "concept_id": "string",
                "concept_en": "string",
                "effort": "Quick | Medium | Involved",
                "hashtags": ["string"],
            }
        ],
        "quick_win": {
            "idea_id": "string",
            "idea_en": "string",
            "why_id": "string",
            "why_en": "string",
            "steps_id": "string",
            "steps_en": "string",
        },
        "avoid": [
            {
                "name_id": "string",
                "name_en": "string",
                "reason_id": "string",
                "reason_en": "string",
            }
        ],
        "insights": {
            "pattern_id": "string",
            "pattern_en": "string",
            "best_posting_hint_id": "string",
            "best_posting_hint_en": "string",
        },
    }

    prompt = {
        "context": {
            "market": "Indonesia",
            "timezone": "WIB (UTC+7)",
            "language": "Bahasa Indonesia + English",
            "user_request": user_request,
        },
        "influencer_profile": profile,
        "user_performance": user_stats,
        "instagram_hashtags": hashtag_data,
        "pinterest_trends": pinterest_trends,
        "apify_trends": apify_trends,
        "competitors": competitor_data,
        "instructions": [
            "Return ONLY valid JSON. No extra text.",
            "Bilingual output: provide Bahasa Indonesia and English fields.",
            "Use only data provided. Do not invent metrics or sources.",
            "If data is missing, use null and write 'data tidak tersedia' / 'data not available'.",
            "Urgency score: 1 (low) to 5 (high). Fit score: 1 to 10.",
            "Return exactly 3 top_trends and 5 content_ideas.",
            "Platform must be one of: Instagram, Pinterest, Both.",
        ],
        "output_schema": output_schema,
    }
    return json.dumps(prompt, ensure_ascii=False, indent=2)


def build_repair_prompt(bad_response: str) -> str:
    repair = {
        "task": "Fix the JSON to match the required schema exactly.",
        "rules": [
            "Return ONLY valid JSON. No extra text.",
            "Bilingual output: provide Bahasa Indonesia and English fields.",
            "Use only the provided data; do not invent metrics.",
            "If data is missing, use null and write 'data tidak tersedia' / 'data not available'.",
            "Return exactly 3 top_trends and 5 content_ideas.",
        ],
        "output_schema": {
            "top_trends": [
                {
                    "name_id": "string",
                    "name_en": "string",
                    "platform": "Instagram | Pinterest | Both",
                    "urgency_score": 1,
                    "urgency_label_id": "string",
                    "urgency_label_en": "string",
                    "fit_score": 1,
                    "evidence": [{"source": "string", "metric": "string", "value": "string"}],
                    "content_angle_id": "string",
                    "content_angle_en": "string",
                }
            ],
            "content_ideas": [
                {
                    "title_id": "string",
                    "title_en": "string",
                    "platform": "string",
                    "hook_id": "string",
                    "hook_en": "string",
                    "concept_id": "string",
                    "concept_en": "string",
                    "effort": "Quick | Medium | Involved",
                    "hashtags": ["string"],
                }
            ],
            "quick_win": {
                "idea_id": "string",
                "idea_en": "string",
                "why_id": "string",
                "why_en": "string",
                "steps_id": "string",
                "steps_en": "string",
            },
            "avoid": [
                {
                    "name_id": "string",
                    "name_en": "string",
                    "reason_id": "string",
                    "reason_en": "string",
                }
            ],
            "insights": {
                "pattern_id": "string",
                "pattern_en": "string",
                "best_posting_hint_id": "string",
                "best_posting_hint_en": "string",
            },
        },
        "bad_response": bad_response,
    }
    return json.dumps(repair, ensure_ascii=False, indent=2)


def validate_result(result: dict) -> None:
    required_top = [
        "name_id",
        "name_en",
        "platform",
        "urgency_score",
        "urgency_label_id",
        "urgency_label_en",
        "fit_score",
        "evidence",
        "content_angle_id",
        "content_angle_en",
    ]
    required_idea = [
        "title_id",
        "title_en",
        "platform",
        "hook_id",
        "hook_en",
        "concept_id",
        "concept_en",
        "effort",
        "hashtags",
    ]
    for key in ["top_trends", "content_ideas", "quick_win", "avoid", "insights"]:
        if key not in result:
            raise ValueError(f"Missing key: {key}")

    if not isinstance(result["top_trends"], list) or len(result["top_trends"]) != 3:
        raise ValueError("top_trends must have exactly 3 items")
    if not isinstance(result["content_ideas"], list) or len(result["content_ideas"]) != 5:
        raise ValueError("content_ideas must have exactly 5 items")

    for trend in result["top_trends"]:
        for key in required_top:
            if key not in trend:
                raise ValueError(f"Missing top_trends field: {key}")

    for idea in result["content_ideas"]:
        for key in required_idea:
            if key not in idea:
                raise ValueError(f"Missing content_ideas field: {key}")

    if not isinstance(result["avoid"], list):
        raise ValueError("avoid must be a list")


def format_report(result: dict) -> str:
    lines: list[str] = []
    lines.append("TOP 3 TRENDS")
    for idx, trend in enumerate(result.get("top_trends", [])[:3], start=1):
        name_id = trend.get("name_id", "data tidak tersedia")
        name_en = trend.get("name_en", "data not available")
        lines.append(f"{idx}. ID: {name_id}")
        lines.append(f"   EN: {name_en}")
        lines.append(f"   Platform: {trend.get('platform', '-')}")
        lines.append(
            f"   Urgency: {trend.get('urgency_score', '-')}/5 | "
            f"ID: {trend.get('urgency_label_id', '-')}; EN: {trend.get('urgency_label_en', '-')}"
        )
        lines.append(f"   Fit Score: {trend.get('fit_score', '-')}/10")
        evidence = trend.get("evidence", [])[:2]
        for ev in evidence:
            metric = ev.get("metric", "-")
            value = ev.get("value", "")
            lines.append(f"   Evidence: {ev.get('source', '-')}: {metric}={value}")
        lines.append(f"   Angle ID: {trend.get('content_angle_id', '-')}")
        lines.append(f"   Angle EN: {trend.get('content_angle_en', '-')}")

    lines.append("")
    lines.append("5 CONTENT IDEAS")
    for idx, idea in enumerate(result.get("content_ideas", [])[:5], start=1):
        lines.append(f"{idx}. ID: {idea.get('title_id', '-')}")
        lines.append(f"   EN: {idea.get('title_en', '-')}")
        lines.append(f"   Platform: {idea.get('platform', '-')}")
        lines.append(f"   Hook ID: {idea.get('hook_id', '-')}")
        lines.append(f"   Hook EN: {idea.get('hook_en', '-')}")
        lines.append(f"   Concept ID: {idea.get('concept_id', '-')}")
        lines.append(f"   Concept EN: {idea.get('concept_en', '-')}")
        lines.append(f"   Effort: {idea.get('effort', '-')}")
        hashtags = idea.get("hashtags", [])
        if hashtags:
            lines.append(f"   Hashtags: {' '.join(hashtags)}")

    lines.append("")
    lines.append("QUICK WIN")
    quick = result.get("quick_win", {})
    lines.append(f"ID: {quick.get('idea_id', '-')}")
    lines.append(f"EN: {quick.get('idea_en', '-')}")
    lines.append(f"Why ID: {quick.get('why_id', '-')}")
    lines.append(f"Why EN: {quick.get('why_en', '-')}")
    lines.append(f"Steps ID: {quick.get('steps_id', '-')}")
    lines.append(f"Steps EN: {quick.get('steps_en', '-')}")

    lines.append("")
    lines.append("AVOID")
    for item in result.get("avoid", []):
        lines.append(f"ID: {item.get('name_id', '-')}")
        lines.append(f"EN: {item.get('name_en', '-')}")
        lines.append(f"Reason ID: {item.get('reason_id', '-')}")
        lines.append(f"Reason EN: {item.get('reason_en', '-')}")

    lines.append("")
    lines.append("INSIGHTS")
    insights = result.get("insights", {})
    lines.append(f"Pattern ID: {insights.get('pattern_id', '-')}")
    lines.append(f"Pattern EN: {insights.get('pattern_en', '-')}")
    lines.append(f"Best Posting Hint ID: {insights.get('best_posting_hint_id', '-')}")
    lines.append(f"Best Posting Hint EN: {insights.get('best_posting_hint_en', '-')}")

    return "\n".join(lines)

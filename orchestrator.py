import json
from typing import Any

from langgraph.graph import StateGraph, END

from apify_client import ApifyClient
from config import (
    APIFY_DATASET_ID,
    DEFAULT_OPENROUTER_MODEL,
    FALLBACK_OPENROUTER_MODEL,
    COMPETITOR_ACCOUNTS,
)
from instagram_api import InstagramClient
from pinterest_api import PinterestClient
from mcp_adapters import LocalMCP
from openrouter_ai import OpenRouterClient
from prompting import SYSTEM_PROMPT, build_strategy_prompt, build_repair_prompt, validate_result, format_report
from utils import summarize_user_media


State = dict[str, Any]


def build_intent_prompt(user_message: str) -> str:
    return json.dumps(
        {
            "task": "Extract intent and constraints from the user message.",
            "rules": [
                "Return ONLY valid JSON.",
                "If unclear, default to: 'content recommendation for today'.",
            ],
            "output_schema": {
                "intent_id": "string",
                "intent_en": "string",
                "constraints": ["string"],
            },
            "user_message": user_message,
        },
        ensure_ascii=False,
        indent=2,
    )


def build_summary_prompt(state: State) -> str:
    return json.dumps(
        {
            "task": "Summarize signals from data for a content strategist.",
            "rules": [
                "Return ONLY valid JSON.",
                "Bilingual output.",
                "Use only provided data.",
            ],
            "output_schema": {
                "audience_id": "string",
                "audience_en": "string",
                "top_themes_id": ["string"],
                "top_themes_en": ["string"],
                "content_formats_id": ["string"],
                "content_formats_en": ["string"],
                "risk_notes_id": ["string"],
                "risk_notes_en": ["string"],
            },
            "data": {
                "profile": state.get("profile"),
                "user_stats": state.get("user_stats"),
                "instagram_hashtags": state.get("instagram_hashtags"),
                "pinterest_trends": state.get("pinterest_trends"),
                "apify_trends": state.get("apify_trends"),
                "competitors": state.get("competitors"),
            },
        },
        ensure_ascii=False,
        indent=2,
    )


def intent_node(state: State) -> State:
    client: OpenRouterClient = state["openrouter"]
    prompt = build_intent_prompt(state["user_message"])
    try:
        raw = client.analyze_trends(prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
        intent = json.loads(raw)
    except Exception:
        intent = {
            "intent_id": "rekomendasi konten hari ini",
            "intent_en": "content recommendations for today",
            "constraints": [],
        }
    state["intent"] = intent
    return state


def data_node(state: State) -> State:
    mcp: LocalMCP = state["mcp"]
    instagram_user_id = state["instagram_user_id"]

    state["profile"] = mcp.tool_instagram_profile(instagram_user_id)
    if state.get("instagram_client"):
        try:
            media = state["instagram_client"].get_user_media(instagram_user_id)
            state["user_stats"] = summarize_user_media(media)
        except Exception as exc:
            state["user_stats"] = {"note": "Instagram media error", "error": str(exc)}
    else:
        state["user_stats"] = {"note": "Instagram client not configured"}

    state["instagram_hashtags"] = mcp.tool_instagram_hashtags(instagram_user_id)
    state["pinterest_trends"] = mcp.tool_pinterest_trends()
    state["apify_trends"] = mcp.tool_apify_trends(state.get("apify_dataset_id", ""))
    competitor_data = []
    if state.get("instagram_client") and COMPETITOR_ACCOUNTS:
        for username in COMPETITOR_ACCOUNTS:
            try:
                raw = state["instagram_client"].business_discovery(instagram_user_id, username)
                competitor_data.append(raw)
            except Exception as exc:
                competitor_data.append({"username": username, "error": str(exc)})
    state["competitors"] = competitor_data
    return state


def summary_node(state: State) -> State:
    client: OpenRouterClient = state["openrouter"]
    prompt = build_summary_prompt(state)
    try:
        raw = client.analyze_trends(prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
        state["signals"] = json.loads(raw)
    except Exception:
        try:
            raw = client.analyze_trends(prompt, model=FALLBACK_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
            state["signals"] = json.loads(raw)
        except Exception:
            state["signals"] = {"note": "summary failed"}
    return state


def strategy_node(state: State) -> State:
    client: OpenRouterClient = state["openrouter"]
    prompt = build_strategy_prompt(
        user_request=state["user_message"],
        profile={**state.get("profile", {}), "signals": state.get("signals")},
        user_stats=state.get("user_stats", {}),
        hashtag_data=state.get("instagram_hashtags", []),
        pinterest_trends=state.get("pinterest_trends", {}),
        apify_trends=state.get("apify_trends", {}),
        competitor_data=state.get("competitors", []),
    )
    try:
        analysis = client.analyze_trends(prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
    except Exception:
        analysis = client.analyze_trends(prompt, model=FALLBACK_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
    state["analysis_raw"] = analysis
    return state


def qa_node(state: State) -> State:
    client: OpenRouterClient = state["openrouter"]
    raw = state.get("analysis_raw", "")
    try:
        parsed = json.loads(raw)
        validate_result(parsed)
        state["analysis_json"] = parsed
    except Exception:
        repair_prompt = build_repair_prompt(raw)
        repaired = client.analyze_trends(repair_prompt, model=DEFAULT_OPENROUTER_MODEL, system_prompt=SYSTEM_PROMPT)
        try:
            parsed = json.loads(repaired)
            validate_result(parsed)
            state["analysis_json"] = parsed
        except Exception:
            state["analysis_json"] = None
    return state


def render_node(state: State) -> State:
    parsed = state.get("analysis_json")
    if isinstance(parsed, dict):
        state["response_text"] = format_report(parsed)
    else:
        state["response_text"] = state.get("analysis_raw", "Maaf, data tidak tersedia.")
    return state


def build_graph() -> StateGraph:
    graph = StateGraph(State)
    graph.add_node("intent", intent_node)
    graph.add_node("data", data_node)
    graph.add_node("summary", summary_node)
    graph.add_node("strategy", strategy_node)
    graph.add_node("qa", qa_node)
    graph.add_node("render", render_node)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "data")
    graph.add_edge("data", "summary")
    graph.add_edge("summary", "strategy")
    graph.add_edge("strategy", "qa")
    graph.add_edge("qa", "render")
    graph.add_edge("render", END)
    return graph


def run_orchestration(
    user_message: str,
    openrouter_api_key: str,
    instagram_access_token: str,
    instagram_user_id: str,
    pinterest_access_token: str | None,
    apify_token: str | None,
) -> str:
    openrouter = OpenRouterClient(api_key=openrouter_api_key)

    instagram_client = InstagramClient(instagram_access_token) if instagram_access_token else None
    pinterest_client = PinterestClient(pinterest_access_token) if pinterest_access_token else None
    apify_client = ApifyClient(apify_token) if apify_token else None

    mcp = LocalMCP(instagram=instagram_client, pinterest=pinterest_client, apify=apify_client)

    graph = build_graph().compile()
    state: State = {
        "user_message": user_message,
        "openrouter": openrouter,
        "instagram_client": instagram_client,
        "instagram_user_id": instagram_user_id,
        "mcp": mcp,
        "apify_dataset_id": APIFY_DATASET_ID,
        "competitors": [],
    }
    final_state = graph.invoke(state)
    return final_state.get("response_text", "Maaf, data tidak tersedia.")

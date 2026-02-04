from prompting import validate_result, format_report


def sample_result():
    return {
        "top_trends": [
            {
                "name_id": "Tren A",
                "name_en": "Trend A",
                "platform": "Instagram",
                "urgency_score": 4,
                "urgency_label_id": "hari ini",
                "urgency_label_en": "today",
                "fit_score": 7,
                "evidence": [{"source": "pinterest", "metric": "growth", "value": "+20%"}],
                "content_angle_id": "Angle A",
                "content_angle_en": "Angle A",
            }
        ] * 3,
        "content_ideas": [
            {
                "title_id": "Ide 1",
                "title_en": "Idea 1",
                "platform": "Instagram",
                "hook_id": "Hook 1",
                "hook_en": "Hook 1",
                "concept_id": "Concept 1",
                "concept_en": "Concept 1",
                "effort": "Quick",
                "hashtags": ["#a", "#b"],
            }
        ] * 5,
        "quick_win": {
            "idea_id": "Quick",
            "idea_en": "Quick",
            "why_id": "Why",
            "why_en": "Why",
            "steps_id": "Steps",
            "steps_en": "Steps",
        },
        "avoid": [
            {"name_id": "Avoid", "name_en": "Avoid", "reason_id": "Reason", "reason_en": "Reason"}
        ],
        "insights": {
            "pattern_id": "Pattern",
            "pattern_en": "Pattern",
            "best_posting_hint_id": "Hint",
            "best_posting_hint_en": "Hint",
        },
    }


def test_validate_result():
    result = sample_result()
    validate_result(result)


def test_format_report():
    result = sample_result()
    text = format_report(result)
    assert "TOP 3 TRENDS" in text
    assert "5 CONTENT IDEAS" in text

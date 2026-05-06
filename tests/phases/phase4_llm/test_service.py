from __future__ import annotations

from unittest.mock import patch

from src.phases.phase1_ingestion.models import BudgetBand, Restaurant
from src.phases.phase2_preferences.models import UserPreferences
from src.phases.phase3_integration.integration import build_integration_output
from src.phases.phase4_llm.groq_client import GroqChatResult, GroqError
from src.phases.phase4_llm.service import recommend_with_llm


def _r(rid: str, name: str, rating: float) -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        location="Bangalore",
        cuisines=["Italian"],
        cost_for_two=800.0,
        budget_band=BudgetBand.MEDIUM,
        rating=rating,
        rating_count=5,
        raw_record=None,
    )


def _prefs() -> UserPreferences:
    return UserPreferences("Bangalore", "medium", ("Italian",), 4.0, None)


def test_recommend_no_candidates() -> None:
    empty = build_integration_output([], _prefs(), candidate_cap=30)
    result = recommend_with_llm(empty, _prefs(), top_n=3)
    assert result.source == "no_candidates"
    assert result.items == ()


@patch("src.phases.phase4_llm.service.chat_completion")
def test_recommend_fallback_on_groq_error(mock_chat) -> None:
    mock_chat.side_effect = GroqError("rate limited", status_code=429)
    restaurants = [_r("1", "A", 4.5), _r("2", "B", 4.3)]
    integration = build_integration_output(restaurants, _prefs(), candidate_cap=10)
    result = recommend_with_llm(integration, _prefs(), top_n=2)
    assert result.source == "fallback"
    assert len(result.items) == 2
    assert result.http_error is not None


@patch("src.phases.phase4_llm.service.chat_completion")
def test_recommend_llm_success(mock_chat) -> None:
    mock_chat.return_value = GroqChatResult(
        content='{"rankings": [{"restaurant_id": "2", "rank": 1, "explanation": "Great Italian"}, {"restaurant_id": "1", "rank": 2, "explanation": "Also good"}]}'
    )
    restaurants = [_r("1", "A", 4.5), _r("2", "B", 4.3)]
    integration = build_integration_output(restaurants, _prefs(), candidate_cap=10)
    result = recommend_with_llm(integration, _prefs(), top_n=2)
    assert result.source == "llm"
    assert len(result.items) == 2
    assert result.items[0].restaurant_id == "2"
    assert "Italian" in result.items[0].explanation or result.items[0].explanation


@patch("src.phases.phase4_llm.service.chat_completion")
def test_recommend_fallback_on_invalid_json(mock_chat) -> None:
    mock_chat.return_value = GroqChatResult(content="not json at all")
    restaurants = [_r("1", "A", 4.5)]
    integration = build_integration_output(restaurants, _prefs(), candidate_cap=10)
    result = recommend_with_llm(integration, _prefs(), top_n=1)
    assert result.source == "fallback"
    assert len(result.items) == 1

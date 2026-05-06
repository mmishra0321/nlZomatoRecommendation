from __future__ import annotations

from src.phases.phase1_ingestion.models import BudgetBand, Restaurant
from src.phases.phase3_integration.integration import build_integration_output
from src.phases.phase3_integration.models import IntegrationOutput, PromptPayload
from src.phases.phase4_llm.models import RankedRecommendation, RecommendationResult
from src.phases.phase5_output.formatter import build_api_response, recommendation_response_to_json
from src.phases.phase5_output.markdown import format_recommendations_markdown
from src.phases.phase2_preferences.models import UserPreferences


def _minimal_payload() -> PromptPayload:
    return PromptPayload(
        system_instructions="x",
        user_preferences_json={},
        candidates_markdown="",
        output_schema_hint="{}",
    )


def test_no_filter_match_empty_integration() -> None:
    prefs = UserPreferences("Void", None, (), 0.0, None)
    integ = build_integration_output([], prefs)
    res = RecommendationResult(source="no_candidates", items=tuple())
    out = build_api_response(integ, res, latency_ms=1.0)
    assert out.empty_state_code == "no_filter_match"
    assert out.items == ()
    assert "No restaurants matched" in out.user_message
    data = out.to_json_dict()
    assert data["telemetry"]["matched_count"] == 0


def test_degraded_model_fallback_with_errors() -> None:
    r = Restaurant(
        id="a",
        name="A",
        location="X",
        cuisines=["Y"],
        cost_for_two=100.0,
        budget_band=BudgetBand.LOW,
        rating=4.0,
        rating_count=1,
        raw_record=None,
    )
    integ = IntegrationOutput(
        has_candidates=True,
        candidates=(r,),
        prompt_payload=_minimal_payload(),
        matched_count=1,
        capped_count=1,
        candidate_cap=30,
    )
    res = RecommendationResult(
        source="fallback",
        items=tuple(),
        http_error="HTTP 503",
    )
    out = build_api_response(integ, res)
    assert out.empty_state_code == "degraded_model"
    assert "backup" in out.user_message.lower() or "Backup" in out.user_message


def test_success_llm_round_trip_json() -> None:
    r = Restaurant(
        id="b",
        name="Bistro",
        location="Town",
        cuisines=["Italian"],
        cost_for_two=500.0,
        budget_band=BudgetBand.MEDIUM,
        rating=4.2,
        rating_count=2,
        raw_record=None,
    )
    integ = IntegrationOutput(
        has_candidates=True,
        candidates=(r,),
        prompt_payload=_minimal_payload(),
        matched_count=1,
        capped_count=1,
        candidate_cap=30,
    )
    item = RankedRecommendation(1, "b", "Bistro", ("Italian",), 4.2, 500.0, "Nice.")
    res = RecommendationResult(source="llm", items=(item,))
    out = build_api_response(integ, res, latency_ms=99.5, telemetry_extra={"model": "test"})
    js = recommendation_response_to_json(out)
    assert "Bistro" in js
    assert out.telemetry.extra.get("model") == "test"
    md = format_recommendations_markdown(out)
    assert "Bistro" in md and "llm" in md.lower()

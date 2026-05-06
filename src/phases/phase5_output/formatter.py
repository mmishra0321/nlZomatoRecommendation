from __future__ import annotations

import json
from typing import Any, Optional

from src.phases.phase3_integration.models import IntegrationOutput
from src.phases.phase4_llm.models import RankedRecommendation, RecommendationResult

from . import empty_states as es
from .models import EmptyStateCode, RecommendationApiResponse, RecommendationItemDTO, TelemetryDTO


def _items_from_phase4(rows: tuple[RankedRecommendation, ...]) -> tuple[RecommendationItemDTO, ...]:
    return tuple(
        RecommendationItemDTO(
            rank=r.rank,
            restaurant_id=r.restaurant_id,
            name=r.name,
            cuisines=r.cuisines,
            rating=r.rating,
            cost_for_two=r.cost_for_two,
            explanation=r.explanation,
        )
        for r in rows
    )


def _resolve_messages(
    integration: IntegrationOutput,
    result: RecommendationResult,
) -> tuple[str, Optional[str], EmptyStateCode]:
    if not integration.has_candidates or result.source == "no_candidates":
        return es.NO_FILTER_MATCH_TITLE, es.NO_FILTER_MATCH_DETAIL, "no_filter_match"

    if result.source == "fallback":
        if result.http_error or result.parse_error:
            return es.DEGRADED_MODEL_TITLE, es.DEGRADED_MODEL_DETAIL, "degraded_model"
        return es.SUCCESS_FALLBACK_TITLE, es.SUCCESS_DETAIL, "ok"

    return es.SUCCESS_LLM_TITLE, es.SUCCESS_DETAIL, "ok"


def build_api_response(
    integration: IntegrationOutput,
    result: RecommendationResult,
    *,
    latency_ms: Optional[float] = None,
    telemetry_extra: Optional[dict[str, Any]] = None,
) -> RecommendationApiResponse:
    """
    Build the canonical UI/API response from Phase 3 + Phase 4 outputs.
    """
    title, detail, code = _resolve_messages(integration, result)
    telemetry = TelemetryDTO(
        latency_ms=latency_ms,
        matched_count=integration.matched_count,
        capped_count=integration.capped_count,
        candidate_cap=integration.candidate_cap,
        extra=dict(telemetry_extra or {}),
    )
    items = _items_from_phase4(result.items)
    return RecommendationApiResponse(
        source=result.source,
        items=items,
        user_message=title,
        detail=detail,
        empty_state_code=code,
        telemetry=telemetry,
        parse_error=result.parse_error,
        http_error=result.http_error,
    )


def recommendation_response_to_json(response: RecommendationApiResponse) -> str:
    return json.dumps(response.to_json_dict(), indent=2)

from __future__ import annotations

import time
from typing import Any

from src.phases.phase2_preferences.service import preferences_from_mapping
from src.phases.phase3_integration.integration import build_integration_output
from src.phases.phase4_llm.service import recommend_with_llm
from src.phases.phase5_output import build_api_response

from backend.app.cache import load_restaurants_cached
from backend.app.config import default_dataset_id
from backend.app.schemas import RecommendationRequest


def run_recommendation(body: RecommendationRequest) -> dict[str, Any]:
    preferences = preferences_from_mapping(body.preferences_payload())
    dataset_id = body.dataset_id or default_dataset_id()
    restaurants, _stats = load_restaurants_cached(dataset_id, body.split, body.dataset_limit)
    integration = build_integration_output(
        restaurants,
        preferences,
        candidate_cap=body.candidate_cap,
    )
    t0 = time.perf_counter()
    result = recommend_with_llm(integration, preferences, top_n=body.top_n)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    response = build_api_response(
        integration,
        result,
        latency_ms=elapsed_ms,
        telemetry_extra={
            "dataset_id": dataset_id,
            "dataset_limit": body.dataset_limit,
            "split": body.split,
        },
    )
    return response.to_json_dict()

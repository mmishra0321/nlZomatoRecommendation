from __future__ import annotations

import json
import os
from typing import Optional

from src.phases.phase1_ingestion.models import Restaurant
from src.phases.phase2_preferences.models import UserPreferences
from src.phases.phase3_integration.models import IntegrationOutput, PromptPayload

from .fallback import deterministic_rankings
from .groq_client import GroqError, chat_completion
from .models import RankedRecommendation, RecommendationResult
from .parser import parse_rankings_payload


def _build_user_content(payload: PromptPayload, preferences: UserPreferences) -> str:
    prefs_json = json.dumps(payload.user_preferences_json, indent=2)
    return (
        "## User preferences (JSON)\n"
        f"{prefs_json}\n\n"
        "## Candidate restaurants (use only these ids)\n"
        f"{payload.candidates_markdown}\n\n"
        "## Output format\n"
        f"{payload.output_schema_hint}\n"
    )


def _restaurant_by_id(candidates: tuple[Restaurant, ...]) -> dict[str, Restaurant]:
    return {r.id: r for r in candidates}


def recommend_with_llm(
    integration: IntegrationOutput,
    preferences: UserPreferences,
    *,
    top_n: int = 5,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout_seconds: float | None = None,
    max_retries: int = 3,
) -> RecommendationResult:
    """
    Call Groq to rank grounded candidates; on failure or empty parse, use deterministic fallback.
    """
    if not integration.has_candidates or not integration.candidates:
        return RecommendationResult(source="no_candidates", items=tuple())

    candidates = integration.candidates
    allowed_ids = {c.id for c in candidates}
    by_id = _restaurant_by_id(candidates)
    payload = integration.prompt_payload
    user_content = _build_user_content(payload, preferences)

    messages = [
        {"role": "system", "content": payload.system_instructions},
        {"role": "user", "content": user_content},
    ]

    timeout = timeout_seconds
    if timeout is None:
        try:
            timeout = float(os.environ.get("REQUEST_TIMEOUT_SECONDS", "25"))
        except ValueError:
            timeout = 25.0

    try:
        groq = chat_completion(
            messages,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout,
            max_retries=max_retries,
        )
    except GroqError as e:
        items = deterministic_rankings(candidates, preferences, top_n)
        return RecommendationResult(
            source="fallback",
            items=items,
            http_error=str(e),
        )
    except Exception as e:  # pragma: no cover - defensive
        items = deterministic_rankings(candidates, preferences, top_n)
        return RecommendationResult(
            source="fallback",
            items=items,
            http_error=str(e),
        )

    raw_text = groq.content
    parsed, parse_err = parse_rankings_payload(raw_text, allowed_ids)

    if parse_err or not parsed:
        items = deterministic_rankings(candidates, preferences, top_n)
        return RecommendationResult(
            source="fallback",
            items=items,
            raw_model_text=raw_text,
            parse_error=parse_err or "Empty rankings after validation.",
        )

    items: list[RankedRecommendation] = []
    for row in parsed[: max(0, top_n)]:
        rid = row["restaurant_id"]
        r = by_id.get(rid)
        if r is None:
            continue
        expl = row.get("explanation") or ""
        if not str(expl).strip():
            expl = deterministic_rankings((r,), preferences, 1)[0].explanation
        items.append(
            RankedRecommendation(
                rank=len(items) + 1,
                restaurant_id=r.id,
                name=r.name,
                cuisines=tuple(r.cuisines),
                rating=r.rating,
                cost_for_two=r.cost_for_two,
                explanation=str(expl).strip(),
            )
        )

    if not items:
        fb = deterministic_rankings(candidates, preferences, top_n)
        return RecommendationResult(
            source="fallback",
            items=fb,
            raw_model_text=raw_text,
            parse_error="No valid grounded rankings after filtering.",
        )

    return RecommendationResult(source="llm", items=tuple(items), raw_model_text=raw_text)

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from src.phases.phase1_ingestion.models import BudgetBand, Restaurant
from src.phases.phase2_preferences.models import UserPreferences

from .models import IntegrationOutput, PromptPayload

DEFAULT_CANDIDATE_CAP = 30


def _location_matches(preference_location: str, restaurant_location: str) -> bool:
    pref = preference_location.casefold().strip()
    loc = restaurant_location.casefold().strip()
    if not pref or not loc:
        return False
    if pref == loc:
        return True
    # Area / substring: e.g. user "Koramangala" vs row "Bangalore Koramangala"
    return pref in loc


def _budget_matches(user_budget: str | None, restaurant: Restaurant) -> bool:
    if user_budget is None:
        return True
    band = restaurant.budget_band
    if band is BudgetBand.UNKNOWN:
        return True
    return band.value == user_budget


def _cuisine_overlap(user_cuisines: tuple[str, ...], restaurant_cuisines: list[str]) -> bool:
    if not user_cuisines:
        return True
    user_set = {c.casefold() for c in user_cuisines}
    rest_set = {c.casefold() for c in restaurant_cuisines}
    return bool(user_set & rest_set)


def _rating_meets(minimum_rating: float, restaurant_rating: float) -> bool:
    return restaurant_rating >= minimum_rating


def filter_and_rank_candidates(
    restaurants: list[Restaurant],
    preferences: UserPreferences,
    candidate_cap: int = DEFAULT_CANDIDATE_CAP,
) -> tuple[list[Restaurant], int]:
    """
    Deterministic hard filters + stable sort + cap.
    Returns (capped_candidates, matched_count_before_cap).
    """
    matched: list[Restaurant] = []
    for r in restaurants:
        if not _location_matches(preferences.location, r.location):
            continue
        if not _budget_matches(preferences.budget, r):
            continue
        if not _cuisine_overlap(preferences.cuisines, r.cuisines):
            continue
        if not _rating_meets(preferences.minimum_rating, r.rating):
            continue
        matched.append(r)

    matched_count = len(matched)
    # Stable sort: higher rating first, then name, then id
    matched.sort(key=lambda x: (-x.rating, x.name.casefold(), x.id))

    cap = max(1, candidate_cap)
    capped = matched[:cap]
    return capped, matched_count


def _preferences_to_json(preferences: UserPreferences) -> dict[str, Any]:
    data = asdict(preferences)
    # Tuple -> list for JSON
    data["cuisines"] = list(preferences.cuisines)
    return data


def _candidates_to_markdown(candidates: tuple[Restaurant, ...]) -> str:
    lines = [
        "| id | name | location | cuisines | rating | cost_for_two | budget_band |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for r in candidates:
        cuisines = ", ".join(r.cuisines)
        cost = "" if r.cost_for_two is None else str(r.cost_for_two)
        lines.append(
            f"| {r.id} | {r.name} | {r.location} | {cuisines} | {r.rating} | {cost} | {r.budget_band.value} |"
        )
    return "\n".join(lines)


OUTPUT_SCHEMA_HINT = """Respond with valid JSON only, no markdown fences, matching this shape:
{
  "rankings": [
    { "restaurant_id": "<id from candidate table>", "rank": 1, "explanation": "<short reason tied to user preferences>" }
  ]
}
Use only restaurant_id values that appear in the candidate table. If none fit, return { \"rankings\": [] }."""


def build_prompt_payload(
    preferences: UserPreferences,
    candidates: tuple[Restaurant, ...],
) -> PromptPayload:
    system_instructions = (
        "You are a restaurant recommendation assistant. "
        "You MUST only recommend restaurants that appear in the provided candidate table. "
        "Do not invent names or ids. Rank the best matches for the user's preferences and explain briefly why each fits."
    )
    user_prefs = _preferences_to_json(preferences)
    table = _candidates_to_markdown(candidates)
    return PromptPayload(
        system_instructions=system_instructions,
        user_preferences_json=user_prefs,
        candidates_markdown=table,
        output_schema_hint=OUTPUT_SCHEMA_HINT,
    )


def build_integration_output(
    restaurants: list[Restaurant],
    preferences: UserPreferences,
    candidate_cap: int = DEFAULT_CANDIDATE_CAP,
) -> IntegrationOutput:
    capped, matched_count = filter_and_rank_candidates(
        restaurants, preferences, candidate_cap=candidate_cap
    )
    candidates_tuple = tuple(capped)
    has_candidates = len(candidates_tuple) > 0
    prompt = build_prompt_payload(preferences, candidates_tuple)
    return IntegrationOutput(
        has_candidates=has_candidates,
        candidates=candidates_tuple,
        prompt_payload=prompt,
        matched_count=matched_count,
        capped_count=len(candidates_tuple),
        candidate_cap=candidate_cap,
    )


def integration_output_to_debug_dict(output: IntegrationOutput) -> dict[str, Any]:
    """Serializable summary for CLI / logs (no raw_record)."""
    return {
        "has_candidates": output.has_candidates,
        "matched_count": output.matched_count,
        "capped_count": output.capped_count,
        "candidate_cap": output.candidate_cap,
        "candidate_ids": [c.id for c in output.candidates],
        "prompt": {
            "system_instructions": output.prompt_payload.system_instructions,
            "user_preferences_json": output.prompt_payload.user_preferences_json,
            "candidates_markdown": output.prompt_payload.candidates_markdown,
            "output_schema_hint": output.prompt_payload.output_schema_hint,
        },
    }


def integration_output_to_json(output: IntegrationOutput) -> str:
    return json.dumps(integration_output_to_debug_dict(output), indent=2)

from __future__ import annotations

from src.phases.phase1_ingestion.models import Restaurant
from src.phases.phase2_preferences.models import UserPreferences

from .models import RankedRecommendation


def _template_explanation(restaurant: Restaurant, preferences: UserPreferences) -> str:
    parts = [
        f"Strong match for {preferences.location}",
        f"rating {restaurant.rating}",
    ]
    if preferences.cuisines:
        overlap = [c for c in restaurant.cuisines if c.casefold() in {x.casefold() for x in preferences.cuisines}]
        if overlap:
            parts.append(f"cuisines include {', '.join(overlap)}")
    if preferences.budget and restaurant.budget_band.value != "unknown":
        parts.append(f"budget band {restaurant.budget_band.value}")
    if preferences.additional_preferences:
        parts.append(f"notes: {preferences.additional_preferences[:120]}")
    return "; ".join(parts) + "."


def deterministic_rankings(
    candidates: tuple[Restaurant, ...],
    preferences: UserPreferences,
    top_n: int,
) -> tuple[RankedRecommendation, ...]:
    """Top-N from pre-sorted candidates (Phase 3 order) with template explanations."""
    n = max(0, top_n)
    items: list[RankedRecommendation] = []
    for i, r in enumerate(candidates[:n], start=1):
        items.append(
            RankedRecommendation(
                rank=i,
                restaurant_id=r.id,
                name=r.name,
                cuisines=tuple(r.cuisines),
                rating=r.rating,
                cost_for_two=r.cost_for_two,
                explanation=_template_explanation(r, preferences),
            )
        )
    return tuple(items)

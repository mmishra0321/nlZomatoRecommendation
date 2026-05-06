from __future__ import annotations

import pytest

from src.phases.phase1_ingestion.models import BudgetBand, Restaurant
from src.phases.phase2_preferences.models import UserPreferences
from src.phases.phase3_integration.integration import (
    build_integration_output,
    build_prompt_payload,
    filter_and_rank_candidates,
)
from src.phases.phase3_integration.models import IntegrationOutput


def _r(
    rid: str,
    name: str,
    location: str,
    cuisines: list[str],
    rating: float,
    band: BudgetBand,
    cost: float | None = 800.0,
) -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        location=location,
        cuisines=cuisines,
        cost_for_two=cost,
        budget_band=band,
        rating=rating,
        rating_count=10,
        raw_record=None,
    )


def test_filter_location_budget_cuisine_rating() -> None:
    restaurants = [
        _r("1", "A", "Bangalore", ["Italian"], 4.5, BudgetBand.MEDIUM),
        _r("2", "B", "Delhi", ["Chinese"], 4.0, BudgetBand.LOW),
        _r("3", "C", "Bangalore", ["Chinese"], 3.5, BudgetBand.MEDIUM),
        _r("4", "D", "Bangalore", ["Italian", "Chinese"], 4.8, BudgetBand.HIGH),
        _r("5", "E", "Bangalore", ["Italian", "North Indian"], 4.2, BudgetBand.MEDIUM),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="medium",
        cuisines=("Italian",),
        minimum_rating=4.0,
    )
    out, matched = filter_and_rank_candidates(restaurants, prefs, candidate_cap=10)
    assert matched == 2
    ids = [x.id for x in out]
    assert ids == ["1", "5"]


def test_filter_no_cuisine_means_no_cuisine_filter() -> None:
    restaurants = [
        _r("1", "A", "Bangalore", ["Thai"], 4.0, BudgetBand.LOW),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget=None,
        cuisines=(),
        minimum_rating=0.0,
    )
    out, matched = filter_and_rank_candidates(restaurants, prefs)
    assert matched == 1
    assert len(out) == 1


def test_filter_unknown_budget_band_passes_when_user_has_budget() -> None:
    restaurants = [
        _r("1", "A", "Bangalore", ["X"], 4.0, BudgetBand.UNKNOWN, cost=None),
    ]
    prefs = UserPreferences(
        location="Bangalore",
        budget="low",
        cuisines=(),
        minimum_rating=0.0,
    )
    out, matched = filter_and_rank_candidates(restaurants, prefs)
    assert matched == 1


def test_cap_stable_order() -> None:
    restaurants = [
        _r(str(i), f"R{i}", "Bangalore", ["X"], 4.0, BudgetBand.LOW) for i in range(5)
    ]
    prefs = UserPreferences("Bangalore", None, (), 0.0)
    out, matched = filter_and_rank_candidates(restaurants, prefs, candidate_cap=3)
    assert matched == 5
    assert len(out) == 3


def test_build_integration_output_no_candidates() -> None:
    prefs = UserPreferences("Mumbai", None, (), 0.0)
    out = build_integration_output([], prefs)
    assert isinstance(out, IntegrationOutput)
    assert out.has_candidates is False
    assert out.candidates == ()
    assert out.matched_count == 0
    assert "rankings" in out.prompt_payload.output_schema_hint


def test_build_prompt_payload_contains_grounding() -> None:
    prefs = UserPreferences("Bangalore", "low", ("Italian",), 4.0, "quiet")
    c = (_r("z1", "Z", "Bangalore", ["Italian"], 4.5, BudgetBand.LOW),)
    p = build_prompt_payload(prefs, c)
    assert "only recommend" in p.system_instructions.lower() or "must" in p.system_instructions.lower()
    assert p.user_preferences_json["location"] == "Bangalore"
    assert "z1" in p.candidates_markdown

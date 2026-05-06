from src.phases.phase1_ingestion.models import BudgetBand
from src.phases.phase1_ingestion.normalize import (
    derive_budget_band,
    make_restaurant_id,
    parse_cost,
    parse_cuisines,
    parse_rating,
)


def test_parse_rating_valid_range() -> None:
    assert parse_rating("4.3") == 4.3
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating(0) == 0.0
    assert parse_rating(5) == 5.0


def test_parse_rating_invalid_range() -> None:
    assert parse_rating("N/A") is None
    assert parse_rating(-1) is None
    assert parse_rating(5.5) is None


def test_parse_cost_varied_formats() -> None:
    assert parse_cost("1,200") == 1200.0
    assert parse_cost("Rs. 450 for two") == 450.0
    assert parse_cost("") is None


def test_parse_cuisines_deduplicates() -> None:
    cuisines = parse_cuisines("Italian, Chinese / italian | North Indian")
    assert cuisines == ["Italian", "Chinese", "North Indian"]


def test_derive_budget_band() -> None:
    assert derive_budget_band(400) == BudgetBand.LOW
    assert derive_budget_band(1000) == BudgetBand.MEDIUM
    assert derive_budget_band(2000) == BudgetBand.HIGH
    assert derive_budget_band(None) == BudgetBand.UNKNOWN


def test_make_restaurant_id_deterministic() -> None:
    first = make_restaurant_id("Cafe Good", "Bangalore")
    second = make_restaurant_id("Cafe Good", "Bangalore")
    assert first == second

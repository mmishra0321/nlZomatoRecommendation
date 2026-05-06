from dataclasses import dataclass

import pytest

from src.phases.phase2_preferences.models import UserPreferences
from src.phases.phase2_preferences.service import (
    PreferenceValidationError,
    allowed_cities_from_restaurants,
    preferences_from_mapping,
)


def test_preferences_from_mapping_valid_payload() -> None:
    payload = {
        "location": " bangalore ",
        "budget": "MEDIUM",
        "cuisines": ["italian", "Chinese", "italian"],
        "minimum_rating": "4.2",
        "additional_preferences": " family friendly  ",
    }

    result = preferences_from_mapping(payload)

    assert isinstance(result, UserPreferences)
    assert result.location == "Bangalore"
    assert result.budget == "medium"
    assert result.cuisines == ("Italian", "Chinese")
    assert result.minimum_rating == 4.2
    assert result.additional_preferences == "family friendly"


def test_preferences_location_required() -> None:
    with pytest.raises(PreferenceValidationError) as exc:
        preferences_from_mapping({"location": " "})
    assert exc.value.errors["location"] == "Location is required."


def test_preferences_reject_invalid_budget() -> None:
    with pytest.raises(PreferenceValidationError) as exc:
        preferences_from_mapping({"location": "Delhi", "budget": "cheap"})
    assert "Budget must be" in exc.value.errors["budget"]


def test_preferences_numeric_budget_maps_to_band() -> None:
    r = preferences_from_mapping({"location": "Delhi", "budget": "2000"})
    assert r.budget == "high"
    r2 = preferences_from_mapping({"location": "Delhi", "budget": "400"})
    assert r2.budget == "low"


def test_preferences_reject_invalid_rating() -> None:
    with pytest.raises(PreferenceValidationError) as exc:
        preferences_from_mapping({"location": "Delhi", "minimum_rating": "8"})
    assert "between 0 and 5" in exc.value.errors["minimum_rating"]


def test_preferences_validate_allowed_city_names() -> None:
    with pytest.raises(PreferenceValidationError) as exc:
        preferences_from_mapping(
            {"location": "Mumbai"},
            allowed_city_names={"Delhi", "Bangalore"},
        )
    assert "Unsupported location" in exc.value.errors["location"]


@dataclass
class _StubRestaurant:
    location: str


def test_allowed_cities_from_restaurants() -> None:
    restaurants = [
        _StubRestaurant(location="bangalore"),
        _StubRestaurant(location="Delhi"),
        _StubRestaurant(location="  delhi "),
    ]
    allowed = allowed_cities_from_restaurants(restaurants)
    assert allowed == {"Bangalore", "Delhi"}

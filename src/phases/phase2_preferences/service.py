from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict
from typing import Any, Optional

from .models import UserPreferences

ALLOWED_BUDGETS = {"low", "medium", "high"}
DEFAULT_MIN_RATING = 0.0
MAX_MIN_RATING = 5.0
MAX_ADDITIONAL_PREF_LENGTH = 500
MAX_CUISINES = 10


class PreferenceValidationError(ValueError):
    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__("Invalid user preferences")


def _normalize_spaces(value: str) -> str:
    return " ".join(value.strip().split())


def _normalize_text(value: str) -> str:
    return _normalize_spaces(value).casefold()


def _titleize(value: str) -> str:
    return " ".join(part.capitalize() for part in _normalize_text(value).split())


def _parse_location(raw: Any, errors: dict[str, str], allowed_city_names: Optional[set[str]]) -> str:
    if raw is None:
        errors["location"] = "Location is required."
        return ""
    location = _titleize(str(raw))
    if not location:
        errors["location"] = "Location is required."
        return ""
    if allowed_city_names is not None and location not in allowed_city_names:
        errors["location"] = f"Unsupported location '{location}'."
    return location


def _cost_to_budget_band(amount: float) -> str:
    """Same bands as Phase 1 `derive_budget_band` for cost-for-two style numbers."""
    if amount <= 500:
        return "low"
    if amount <= 1500:
        return "medium"
    return "high"


def _parse_budget(raw: Any, errors: dict[str, str]) -> Optional[str]:
    if raw is None or str(raw).strip() == "":
        return None
    s = str(raw).strip()
    budget = _normalize_text(s)
    if budget in ALLOWED_BUDGETS:
        return budget
    try:
        amount = float(s.replace(",", ""))
        if amount > 0:
            return _cost_to_budget_band(amount)
    except ValueError:
        pass
    errors["budget"] = "Budget must be low, medium, high, or a positive number (typical cost for two)."
    return None


def _to_cuisine_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [part.strip() for part in raw.replace("/", ",").split(",")]
    if isinstance(raw, Iterable):
        return [str(item).strip() for item in raw]
    return [str(raw).strip()]


def _parse_cuisines(raw: Any, errors: dict[str, str]) -> tuple[str, ...]:
    values = _to_cuisine_list(raw)
    seen: set[str] = set()
    parsed: list[str] = []
    for value in values:
        if not value:
            continue
        cuisine = _titleize(value)
        if not cuisine or cuisine in seen:
            continue
        parsed.append(cuisine)
        seen.add(cuisine)

    if len(parsed) > MAX_CUISINES:
        errors["cuisines"] = f"At most {MAX_CUISINES} cuisines are allowed."
        return tuple(parsed[:MAX_CUISINES])
    return tuple(parsed)


def _parse_minimum_rating(raw: Any, errors: dict[str, str]) -> float:
    if raw is None or str(raw).strip() == "":
        return DEFAULT_MIN_RATING
    try:
        rating = float(str(raw).strip())
    except ValueError:
        errors["minimum_rating"] = "Minimum rating must be a number between 0 and 5."
        return DEFAULT_MIN_RATING
    if rating < 0 or rating > MAX_MIN_RATING:
        errors["minimum_rating"] = "Minimum rating must be between 0 and 5."
        return DEFAULT_MIN_RATING
    return round(rating, 2)


def _parse_additional_preferences(raw: Any, errors: dict[str, str]) -> Optional[str]:
    if raw is None:
        return None
    value = _normalize_spaces(str(raw))
    if not value:
        return None
    if len(value) > MAX_ADDITIONAL_PREF_LENGTH:
        errors["additional_preferences"] = (
            f"Additional preferences cannot exceed {MAX_ADDITIONAL_PREF_LENGTH} characters."
        )
        return value[:MAX_ADDITIONAL_PREF_LENGTH]
    return value


def preferences_from_mapping(
    payload: Mapping[str, Any],
    allowed_city_names: Optional[set[str]] = None,
) -> UserPreferences:
    errors: dict[str, str] = {}

    location = _parse_location(payload.get("location"), errors, allowed_city_names)
    budget = _parse_budget(payload.get("budget"), errors)
    cuisines = _parse_cuisines(payload.get("cuisines"), errors)
    minimum_rating = _parse_minimum_rating(payload.get("minimum_rating"), errors)
    additional_preferences = _parse_additional_preferences(
        payload.get("additional_preferences"),
        errors,
    )

    if errors:
        raise PreferenceValidationError(errors)

    return UserPreferences(
        location=location,
        budget=budget,
        cuisines=cuisines,
        minimum_rating=minimum_rating,
        additional_preferences=additional_preferences,
    )


def allowed_cities_from_restaurants(restaurants: Iterable[Any]) -> set[str]:
    cities: set[str] = set()
    for restaurant in restaurants:
        location = getattr(restaurant, "location", None)
        if location:
            cities.add(_titleize(str(location)))
    return cities


def preferences_to_dict(preferences: UserPreferences) -> dict[str, Any]:
    return asdict(preferences)

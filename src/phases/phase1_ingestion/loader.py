from __future__ import annotations

from itertools import islice
from dataclasses import dataclass, field
from typing import Any

from datasets import load_dataset

from .models import Restaurant
from .normalize import (
    derive_budget_band,
    make_restaurant_id,
    parse_cost,
    parse_cuisines,
    parse_rating,
    parse_rating_count,
    titleize_text,
)

DEFAULT_DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DEFAULT_SPLIT = "train"


@dataclass
class IngestionStats:
    total_rows: int = 0
    valid_rows: int = 0
    dropped_rows: int = 0
    drop_reasons: dict[str, int] = field(default_factory=dict)

    def add_drop(self, reason: str) -> None:
        self.dropped_rows += 1
        self.drop_reasons[reason] = self.drop_reasons.get(reason, 0) + 1


def _pick_first(record: dict[str, Any], candidates: list[str]) -> Any:
    for key in candidates:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def _compose_location(record: dict[str, Any]) -> Any:
    """City + area when both exist (HF schema: listed_in(city) + location; legacy: City + Locality)."""
    city = _pick_first(record, ["listed_in(city)", "City", "city"])
    area = _pick_first(record, ["location", "Location", "Locality", "locality", "Area", "area"])
    if city and area:
        c, a = str(city).strip(), str(area).strip()
        if a.casefold() != c.casefold():
            return f"{c}, {a}"
    if city:
        return city
    if area:
        return area
    return _pick_first(record, ["Location", "location"])


def _map_record_to_restaurant(record: dict[str, Any], stats: IngestionStats) -> Restaurant | None:
    name = _pick_first(record, ["Restaurant Name", "name", "restaurant_name"])
    location = _compose_location(record)
    cuisines_raw = _pick_first(record, ["Cuisines", "cuisines", "Cuisine", "cuisine"])
    cost_raw = _pick_first(
        record,
        [
            "approx_cost(for two people)",
            "Average Cost for two",
            "cost_for_two",
            "Cost",
            "average_cost_for_two",
        ],
    )
    rating_raw = _pick_first(record, ["rate", "Aggregate rating", "rating", "Rating"])
    rating_count_raw = _pick_first(record, ["votes", "Votes", "rating_count"])

    if not name:
        stats.add_drop("missing_name")
        return None
    if not location:
        stats.add_drop("missing_location")
        return None

    cuisines = parse_cuisines(cuisines_raw)
    if not cuisines:
        stats.add_drop("missing_cuisines")
        return None

    rating = parse_rating(rating_raw)
    if rating is None:
        stats.add_drop("invalid_rating")
        return None

    cost_for_two = parse_cost(cost_raw)
    rating_count = parse_rating_count(rating_count_raw)

    normalized_name = titleize_text(str(name))
    normalized_location = titleize_text(str(location))
    restaurant_id = make_restaurant_id(normalized_name, normalized_location)

    return Restaurant(
        id=restaurant_id,
        name=normalized_name,
        location=normalized_location,
        cuisines=cuisines,
        cost_for_two=cost_for_two,
        budget_band=derive_budget_band(cost_for_two),
        rating=rating,
        rating_count=rating_count,
        raw_record=record,
    )


def iter_restaurants(
    dataset_id: str = DEFAULT_DATASET_ID,
    split: str = DEFAULT_SPLIT,
    limit: int | None = None,
    keep_raw_record: bool = False,
) -> tuple[list[Restaurant], IngestionStats]:
    stats = IngestionStats()
    if limit is not None:
        # Streaming avoids loading the full HF split in memory (important on
        # small deployment instances like Railway free/shared containers).
        dataset = load_dataset(dataset_id, split=split, streaming=True)
        rows = islice(dataset, max(limit, 0))
    else:
        dataset = load_dataset(dataset_id, split=split)
        rows = dataset

    dedupe_keys: set[tuple[str, str]] = set()
    restaurants: list[Restaurant] = []

    for row in rows:
        stats.total_rows += 1
        restaurant = _map_record_to_restaurant(dict(row), stats)
        if restaurant is None:
            continue

        dedupe_key = (restaurant.name.casefold(), restaurant.location.casefold())
        if dedupe_key in dedupe_keys:
            stats.add_drop("duplicate_name_location")
            continue

        dedupe_keys.add(dedupe_key)
        if not keep_raw_record:
            restaurant = Restaurant(
                id=restaurant.id,
                name=restaurant.name,
                location=restaurant.location,
                cuisines=restaurant.cuisines,
                cost_for_two=restaurant.cost_for_two,
                budget_band=restaurant.budget_band,
                rating=restaurant.rating,
                rating_count=restaurant.rating_count,
                raw_record=None,
            )
        restaurants.append(restaurant)
        stats.valid_rows += 1

    return restaurants, stats


def load_restaurants(
    dataset_id: str = DEFAULT_DATASET_ID,
    split: str = DEFAULT_SPLIT,
    limit: int | None = None,
) -> list[Restaurant]:
    restaurants, _ = iter_restaurants(
        dataset_id=dataset_id,
        split=split,
        limit=limit,
        keep_raw_record=False,
    )
    return restaurants

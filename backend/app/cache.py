from __future__ import annotations

from src.phases.phase1_ingestion.loader import IngestionStats, iter_restaurants
from src.phases.phase1_ingestion.models import Restaurant

# In-process cache keyed by dataset slice (single-worker dev servers).
_restaurant_cache: dict[tuple[str, str, int], tuple[list[Restaurant], IngestionStats]] = {}


def clear_restaurant_cache() -> None:
    """For tests."""
    _restaurant_cache.clear()


def load_restaurants_cached(
    dataset_id: str,
    split: str,
    limit: int,
) -> tuple[list[Restaurant], IngestionStats]:
    key = (dataset_id, split, limit)
    if key not in _restaurant_cache:
        restaurants, stats = iter_restaurants(
            dataset_id=dataset_id,
            split=split,
            limit=limit,
        )
        _restaurant_cache[key] = (restaurants, stats)
    return _restaurant_cache[key]

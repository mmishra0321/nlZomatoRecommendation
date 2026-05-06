from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class BudgetBand(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Restaurant:
    id: str
    name: str
    location: str
    cuisines: list[str]
    cost_for_two: float | None
    budget_band: BudgetBand
    rating: float
    rating_count: int | None
    raw_record: dict[str, Any] | None = None

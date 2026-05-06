from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

RecommendationSource = Literal["llm", "fallback", "no_candidates"]


@dataclass(frozen=True)
class RankedRecommendation:
    """One display row after Phase 4 (aligned with problem statement output fields)."""

    rank: int
    restaurant_id: str
    name: str
    cuisines: tuple[str, ...]
    rating: float
    cost_for_two: Optional[float]
    explanation: str


@dataclass(frozen=True)
class RecommendationResult:
    source: RecommendationSource
    items: tuple[RankedRecommendation, ...]
    raw_model_text: Optional[str] = None
    parse_error: Optional[str] = None
    http_error: Optional[str] = None

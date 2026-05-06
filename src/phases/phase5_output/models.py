from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

EmptyStateCode = Literal["ok", "no_filter_match", "degraded_model"]


@dataclass(frozen=True)
class RecommendationItemDTO:
    """One row in the UI/API response (problem statement fields)."""

    rank: int
    restaurant_id: str
    name: str
    cuisines: tuple[str, ...]
    rating: float
    cost_for_two: Optional[float]
    explanation: str


@dataclass(frozen=True)
class TelemetryDTO:
    """Non-sensitive request metadata for logs and UI diagnostics."""

    latency_ms: Optional[float] = None
    matched_count: int = 0
    capped_count: int = 0
    candidate_cap: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationApiResponse:
    """
    Canonical Phase 5 payload for CLI, HTTP API (Phase 6), and frontend (Phase 7).
    """

    source: Literal["llm", "fallback", "no_candidates"]
    items: tuple[RecommendationItemDTO, ...]
    user_message: str
    detail: Optional[str]
    empty_state_code: EmptyStateCode
    telemetry: TelemetryDTO
    parse_error: Optional[str] = None
    http_error: Optional[str] = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "items": [
                {
                    "rank": i.rank,
                    "restaurant_id": i.restaurant_id,
                    "name": i.name,
                    "cuisines": list(i.cuisines),
                    "rating": i.rating,
                    "cost_for_two": i.cost_for_two,
                    "explanation": i.explanation,
                }
                for i in self.items
            ],
            "user_message": self.user_message,
            "detail": self.detail,
            "empty_state_code": self.empty_state_code,
            "telemetry": {
                "latency_ms": self.telemetry.latency_ms,
                "matched_count": self.telemetry.matched_count,
                "capped_count": self.telemetry.capped_count,
                "candidate_cap": self.telemetry.candidate_cap,
                **self.telemetry.extra,
            },
            "parse_error": self.parse_error,
            "http_error": self.http_error,
        }

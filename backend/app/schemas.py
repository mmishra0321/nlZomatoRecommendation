from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel, Field, field_validator

from backend.app.config import (
    DEFAULT_CANDIDATE_CAP,
    DEFAULT_DATASET_LIMIT,
    MAX_CANDIDATE_CAP,
    MAX_DATASET_LIMIT,
    MAX_TOP_N,
    MIN_DATASET_LIMIT,
)


class RecommendationRequest(BaseModel):
    """Maps to Phase 2 `preferences_from_mapping` plus Phase 6 safety knobs."""

    location: str = Field(..., min_length=1, max_length=200)
    minimum_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    budget: Optional[Union[str, float]] = None
    cuisines: list[str] = Field(default_factory=list)
    additional_preferences: Optional[str] = Field(default=None, max_length=600)

    top_n: int = Field(default=5, ge=1, le=MAX_TOP_N)
    dataset_limit: int = Field(
        default=DEFAULT_DATASET_LIMIT,
        ge=MIN_DATASET_LIMIT,
        le=MAX_DATASET_LIMIT,
    )
    candidate_cap: int = Field(default=DEFAULT_CANDIDATE_CAP, ge=1, le=MAX_CANDIDATE_CAP)
    dataset_id: Optional[str] = None
    split: str = Field(default="train", max_length=32)

    model_config = {"extra": "ignore"}

    @field_validator("cuisines", mode="before")
    @classmethod
    def _coerce_cuisines(cls, v: Any) -> Any:
        return v if v is not None else []

    def preferences_payload(self) -> dict[str, Any]:
        """Phase 2 validation expects string-ish budget; coerce numbers."""
        budget_val = self.budget
        if isinstance(budget_val, float):
            budget_val = str(int(budget_val)) if budget_val.is_integer() else str(budget_val)
        elif isinstance(budget_val, int):
            budget_val = str(budget_val)
        return {
            "location": self.location,
            "budget": budget_val,
            "cuisines": list(self.cuisines),
            "minimum_rating": self.minimum_rating,
            "additional_preferences": self.additional_preferences,
        }

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class UserPreferences:
    location: str
    budget: Optional[str]
    cuisines: Tuple[str, ...]
    minimum_rating: float
    additional_preferences: Optional[str] = None

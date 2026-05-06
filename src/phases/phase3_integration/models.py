from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.phases.phase1_ingestion.models import Restaurant
from src.phases.phase2_preferences.models import UserPreferences


@dataclass(frozen=True)
class PromptPayload:
    """Structured content for the LLM (Phase 4); inspectable and deterministic given inputs."""

    system_instructions: str
    user_preferences_json: dict[str, Any]
    candidates_markdown: str
    output_schema_hint: str


@dataclass(frozen=True)
class IntegrationOutput:
    """Result of Phase 3 before any LLM call."""

    has_candidates: bool
    candidates: tuple[Restaurant, ...]
    prompt_payload: PromptPayload
    matched_count: int
    capped_count: int
    candidate_cap: int

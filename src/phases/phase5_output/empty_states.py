"""User-facing copy for empty and degraded paths (Phase 5 UX semantics)."""

from __future__ import annotations

NO_FILTER_MATCH_TITLE = "No restaurants matched your filters."
NO_FILTER_MATCH_DETAIL = (
    "Try a broader location, a lower minimum rating, fewer cuisine filters, "
    "or a different budget band."
)

DEGRADED_MODEL_TITLE = "Showing backup rankings."
DEGRADED_MODEL_DETAIL = (
    "The AI service was unavailable or returned an unexpected response. "
    "These picks are based on your filters and ratings only."
)

SUCCESS_LLM_TITLE = "Here are your personalized recommendations."
SUCCESS_FALLBACK_TITLE = "Here are top picks based on your filters."
SUCCESS_DETAIL: str | None = None

from __future__ import annotations

from .models import RecommendationApiResponse


def format_recommendations_markdown(response: RecommendationApiResponse) -> str:
    """Human-readable Markdown for demos, logs, or copy-to-clipboard UX."""
    lines = [
        f"## Recommendations ({response.source})",
        "",
        response.user_message,
        "",
    ]
    if response.detail:
        lines.extend([response.detail, ""])
    if not response.items:
        lines.append("_No rows to display._")
        return "\n".join(lines)

    lines.extend(
        [
            "| # | Restaurant | Cuisines | Rating | Cost (2) | Why |",
            "|---|------------|----------|-------:|---------:|-----|",
        ]
    )
    for i in response.items:
        cuisines = ", ".join(i.cuisines)
        cost = "" if i.cost_for_two is None else str(i.cost_for_two)
        expl = i.explanation.replace("|", "\\|")
        lines.append(
            f"| {i.rank} | {i.name} | {cuisines} | {i.rating} | {cost} | {expl} |"
        )
    lines.extend(["", f"_Telemetry: matched={response.telemetry.matched_count}, cap={response.telemetry.candidate_cap}_"])
    return "\n".join(lines)

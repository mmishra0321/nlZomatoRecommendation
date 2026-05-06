from __future__ import annotations

import json
import re
from typing import Any

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse first JSON object from model output; tolerate markdown fences."""
    raw = text.strip()
    if not raw:
        return None
    m = _JSON_FENCE_RE.search(raw)
    if m:
        raw = m.group(1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to find outermost { ... } for rankings
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            data = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return None
    return data if isinstance(data, dict) else None


def parse_rankings_payload(
    text: str,
    allowed_ids: set[str],
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Returns (valid_ranking_dicts, error_message).
    Each dict: restaurant_id, rank, explanation (strings/ints coerced).
    """
    data = extract_json_object(text)
    if data is None:
        return [], "Could not parse JSON from model output."

    rankings = data.get("rankings")
    if rankings is None:
        return [], "Missing 'rankings' key in JSON."

    if not isinstance(rankings, list):
        return [], "'rankings' must be a list."

    cleaned: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in rankings:
        if not isinstance(item, dict):
            continue
        rid = item.get("restaurant_id")
        if rid is None or str(rid) not in allowed_ids:
            continue
        rid_s = str(rid)
        if rid_s in seen_ids:
            continue
        seen_ids.add(rid_s)
        rank = item.get("rank")
        try:
            rank_i = int(rank) if rank is not None else len(cleaned) + 1
        except (TypeError, ValueError):
            rank_i = len(cleaned) + 1
        expl = item.get("explanation")
        expl_s = str(expl).strip() if expl is not None else ""
        cleaned.append(
            {
                "restaurant_id": rid_s,
                "rank": rank_i,
                "explanation": expl_s,
            }
        )

    cleaned.sort(key=lambda x: (x["rank"], x["restaurant_id"]))
    return cleaned, None

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable

from .models import BudgetBand

_CUISINE_SPLIT_RE = re.compile(r"[,/|]")
_NON_NUMERIC_RE = re.compile(r"[^0-9.]")
_FIRST_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split()).casefold()


def titleize_text(value: str) -> str:
    return " ".join(token.capitalize() for token in normalize_text(value).split())


def parse_rating(value: object) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    # Hugging Face Zomato schema often uses "4.1/5" style strings
    m = re.match(r"^(\d+(?:\.\d+)?)", raw)
    if m:
        try:
            rating = float(m.group(1))
        except ValueError:
            rating = None
        else:
            if 0 <= rating <= 5:
                return round(rating, 2)
    try:
        rating = float(raw)
    except ValueError:
        return None

    if rating < 0 or rating > 5:
        return None
    return round(rating, 2)


def parse_rating_count(value: object) -> int | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    cleaned = _NON_NUMERIC_RE.sub("", raw)
    if not cleaned:
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def parse_cost(value: object) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if not raw:
        return None

    match = _FIRST_NUMBER_RE.search(raw)
    if not match:
        return None
    cleaned = match.group(0).replace(",", "")
    try:
        cost = float(cleaned)
    except ValueError:
        return None
    if cost <= 0:
        return None
    return round(cost, 2)


def derive_budget_band(cost_for_two: float | None) -> BudgetBand:
    if cost_for_two is None:
        return BudgetBand.UNKNOWN
    if cost_for_two <= 500:
        return BudgetBand.LOW
    if cost_for_two <= 1500:
        return BudgetBand.MEDIUM
    return BudgetBand.HIGH


def parse_cuisines(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_items = _CUISINE_SPLIT_RE.split(value)
    elif isinstance(value, Iterable):
        raw_items = [str(item) for item in value]
    else:
        raw_items = [str(value)]

    result: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        normalized = titleize_text(item)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def make_restaurant_id(name: str, location: str) -> str:
    payload = f"{normalize_text(name)}|{normalize_text(location)}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    safe_name = normalize_text(name).replace(" ", "-")
    safe_location = normalize_text(location).replace(" ", "-")
    return f"{safe_name}-{safe_location}-{digest}"

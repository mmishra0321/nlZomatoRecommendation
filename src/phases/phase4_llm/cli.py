from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.phases.phase1_ingestion.loader import iter_restaurants
from src.phases.phase2_preferences.service import PreferenceValidationError, preferences_from_mapping
from src.phases.phase3_integration.integration import build_integration_output

from .dotenv import load_dotenv
from .models import RankedRecommendation
from .service import recommend_with_llm


def _ranked_to_dict(r: RankedRecommendation) -> dict:
    return {
        "rank": r.rank,
        "restaurant_id": r.restaurant_id,
        "name": r.name,
        "cuisines": list(r.cuisines),
        "rating": r.rating,
        "cost_for_two": r.cost_for_two,
        "explanation": r.explanation,
    }


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="phase4-llm",
        description="Phase 4: Groq LLM recommendations with fallback",
    )
    sub = p.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("recommend", help="End-to-end: load data, integrate, call Groq (or fallback)")
    rec.add_argument("--location", required=True)
    rec.add_argument("--budget", default=None)
    rec.add_argument("--cuisines", nargs="*", default=[])
    rec.add_argument("--minimum-rating", default=None)
    rec.add_argument("--additional-preferences", default=None)
    rec.add_argument("--candidate-cap", type=int, default=30)
    rec.add_argument("--dataset-limit", type=int, default=5000)
    rec.add_argument("--dataset-id", default=None)
    rec.add_argument("--split", default="train")
    rec.add_argument("--top-n", type=int, default=5)
    rec.add_argument("--fallback-only", action="store_true", help="Skip Groq; use deterministic ranking only")
    return p


def _cmd_recommend(args: argparse.Namespace) -> int:
    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    payload = {
        "location": args.location,
        "budget": args.budget,
        "cuisines": args.cuisines or [],
        "minimum_rating": args.minimum_rating,
        "additional_preferences": args.additional_preferences,
    }
    try:
        preferences = preferences_from_mapping(payload)
    except PreferenceValidationError as exc:
        json.dump({"errors": exc.errors}, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 2

    kwargs: dict = {"split": args.split, "limit": args.dataset_limit}
    if args.dataset_id:
        kwargs["dataset_id"] = args.dataset_id

    restaurants, _ = iter_restaurants(**kwargs)
    integration = build_integration_output(
        restaurants,
        preferences,
        candidate_cap=args.candidate_cap,
    )

    if args.fallback_only:
        from .fallback import deterministic_rankings

        items = deterministic_rankings(integration.candidates, preferences, args.top_n)
        out = {
            "source": "fallback",
            "items": [_ranked_to_dict(x) for x in items],
            "has_candidates": integration.has_candidates,
            "matched_count": integration.matched_count,
        }
        json.dump(out, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    result = recommend_with_llm(integration, preferences, top_n=args.top_n)
    out: dict = {
        "source": result.source,
        "items": [_ranked_to_dict(x) for x in result.items],
        "has_candidates": integration.has_candidates,
        "matched_count": integration.matched_count,
        "parse_error": result.parse_error,
        "http_error": result.http_error,
    }
    if result.raw_model_text is not None:
        out["llm_raw_text"] = result.raw_model_text
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "recommend":
        return _cmd_recommend(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

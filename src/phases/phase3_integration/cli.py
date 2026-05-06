from __future__ import annotations

import argparse
import json
import sys
from src.phases.phase1_ingestion.loader import iter_restaurants
from src.phases.phase2_preferences.service import PreferenceValidationError, preferences_from_mapping

from .integration import build_integration_output, integration_output_to_debug_dict


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase3-integration",
        description="Phase 3: filter restaurants and build LLM prompt payload",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser(
        "prompt-build",
        help="Load dataset (optional limit), apply preferences, print integration JSON",
    )
    build.add_argument("--location", required=True)
    build.add_argument("--budget", default=None)
    build.add_argument("--cuisines", nargs="*", default=[])
    build.add_argument("--minimum-rating", default=None)
    build.add_argument("--additional-preferences", default=None)
    build.add_argument("--candidate-cap", type=int, default=30)
    build.add_argument("--dataset-limit", type=int, default=5000, help="Max rows to scan from HF")
    build.add_argument("--dataset-id", default=None)
    build.add_argument("--split", default="train")
    return parser


def _cmd_prompt_build(args: argparse.Namespace) -> int:
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

    restaurants, _stats = iter_restaurants(**kwargs)
    output = build_integration_output(
        restaurants,
        preferences,
        candidate_cap=args.candidate_cap,
    )
    json.dump(integration_output_to_debug_dict(output), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "prompt-build":
        return _cmd_prompt_build(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

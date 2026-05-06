from __future__ import annotations

import argparse
import json
import sys

from .service import PreferenceValidationError, preferences_from_mapping, preferences_to_dict


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase2-preferences",
        description="Phase 2 preference parsing and validation tools",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse = subparsers.add_parser("prefs-parse", help="Parse and validate preferences")
    parse.add_argument("--location", required=True)
    parse.add_argument("--budget")
    parse.add_argument("--cuisines", nargs="*", default=[])
    parse.add_argument("--minimum-rating")
    parse.add_argument("--additional-preferences")
    return parser


def _cmd_prefs_parse(args: argparse.Namespace) -> int:
    payload = {
        "location": args.location,
        "budget": args.budget,
        "cuisines": args.cuisines,
        "minimum_rating": args.minimum_rating,
        "additional_preferences": args.additional_preferences,
    }
    try:
        preferences = preferences_from_mapping(payload)
    except PreferenceValidationError as exc:
        json.dump({"errors": exc.errors}, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 2

    json.dump(preferences_to_dict(preferences), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "prefs-parse":
        return _cmd_prefs_parse(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

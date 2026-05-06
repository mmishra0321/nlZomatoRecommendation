import argparse
import json
import sys
from dataclasses import asdict

from .loader import DEFAULT_DATASET_ID, DEFAULT_SPLIT, iter_restaurants


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase1-ingestion",
        description="Phase 1 dataset ingestion utilities",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    smoke = subparsers.add_parser("ingest-smoke", help="Run ingestion smoke test")
    smoke.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    smoke.add_argument("--split", default=DEFAULT_SPLIT)
    smoke.add_argument("--limit", type=int, default=25)
    smoke.add_argument("--preview", type=int, default=3)
    return parser


def _cmd_ingest_smoke(args: argparse.Namespace) -> int:
    restaurants, stats = iter_restaurants(
        dataset_id=args.dataset_id,
        split=args.split,
        limit=args.limit,
    )
    preview = [asdict(restaurant) for restaurant in restaurants[: args.preview]]
    payload = {
        "stats": asdict(stats),
        "preview_count": len(preview),
        "preview": preview,
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    if args.command == "ingest-smoke":
        return _cmd_ingest_smoke(args)
    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Smoke: format Phase 4 result through Phase 5 (no network)."""

from __future__ import annotations

import argparse
import sys

from src.phases.phase1_ingestion.models import BudgetBand, Restaurant
from src.phases.phase2_preferences.models import UserPreferences
from src.phases.phase3_integration.integration import build_integration_output
from src.phases.phase3_integration.models import IntegrationOutput, PromptPayload
from src.phases.phase4_llm.models import RankedRecommendation, RecommendationResult

from .formatter import build_api_response, recommendation_response_to_json


def _demo_success() -> tuple[IntegrationOutput, RecommendationResult]:
    item = RankedRecommendation(
        rank=1,
        restaurant_id="demo-1",
        name="Demo Bistro",
        cuisines=("Italian",),
        rating=4.5,
        cost_for_two=900.0,
        explanation="Great Italian near you.",
    )
    r = Restaurant(
        id="demo-1",
        name="Demo Bistro",
        location="Demo City",
        cuisines=["Italian"],
        cost_for_two=900.0,
        budget_band=BudgetBand.MEDIUM,
        rating=4.5,
        rating_count=10,
        raw_record=None,
    )
    payload = PromptPayload(
        system_instructions="demo",
        user_preferences_json={"location": "Demo City"},
        candidates_markdown="| demo |",
        output_schema_hint="{}",
    )
    integ = IntegrationOutput(
        has_candidates=True,
        candidates=(r,),
        prompt_payload=payload,
        matched_count=1,
        capped_count=1,
        candidate_cap=30,
    )
    result = RecommendationResult(source="llm", items=(item,))
    return integ, result


def main() -> int:
    parser = argparse.ArgumentParser(prog="phase5-output", description="Phase 5 output formatting")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo-json", help="Print sample Phase 5 JSON (offline)")
    demo.add_argument("--no-candidates", action="store_true", help="Demo empty-state instead of success")
    args = parser.parse_args()

    if args.cmd == "demo-json":
        if args.no_candidates:
            prefs = UserPreferences("Nowhere", None, (), 0.0, None)
            integ = build_integration_output([], prefs)
            res = RecommendationResult(source="no_candidates", items=tuple())
            out = build_api_response(integ, res, latency_ms=12.3)
        else:
            integ, res = _demo_success()
            out = build_api_response(integ, res, latency_ms=42.0)
        sys.stdout.write(recommendation_response_to_json(out) + "\n")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

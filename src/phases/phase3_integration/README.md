# Phase 3: Integration Layer (Filtering + Prompt Preparation)

Implements `phased-architecture.md` Phase 3:

- **Deterministic filters:** location (exact or substring), optional budget band, optional cuisine overlap, minimum rating
- **Stable ranking:** higher rating first, then name, then id
- **Candidate cap:** default 30 (configurable)
- **Prompt payload:** system instructions, preferences JSON, candidate markdown table, JSON output hint for Phase 4

## API

- `filter_and_rank_candidates(restaurants, preferences, candidate_cap)` → `(list[Restaurant], matched_count)`
- `build_prompt_payload(preferences, candidates)` → `PromptPayload`
- `build_integration_output(restaurants, preferences, candidate_cap)` → `IntegrationOutput`
- `integration_output_to_debug_dict(output)` / `integration_output_to_json(output)` for CLI/logging

## CLI (`prompt-build`)

Requires repo root on `PYTHONPATH` (run from project root):

```bash
source .venv/bin/activate
pip install -r src/phases/phase1_ingestion/requirements.txt
python -m src.phases.phase3_integration.cli prompt-build \
  --location Bangalore \
  --budget medium \
  --cuisines Italian \
  --minimum-rating 4.0 \
  --dataset-limit 2000 \
  --candidate-cap 30
```

## Dependencies

Phase 3 imports Phase 1 (`Restaurant`, `iter_restaurants` in CLI) and Phase 2 (`UserPreferences`, `preferences_from_mapping` in CLI).

## Exit criteria

- Same inputs → same candidate order (deterministic sort keys)
- No-match: `has_candidates=False`, empty candidates, prompt still well-formed for optional LLM refusal handling in Phase 4

# Phase 4: LLM Recommendation Engine (Groq)

Implements `phased-architecture.md` Phase 4:

- **Groq** OpenAI-compatible chat completions (`GROQ_API_KEY`, optional `GROQ_MODEL`)
- **Structured JSON** response with `rankings[]` (`restaurant_id`, `rank`, `explanation`)
- **Parser** with markdown-fence tolerance and **grounding** (only ids from Phase 3 candidates)
- **Retries** on 429 / 5xx with backoff (`groq_client.chat_completion`)
- **Fallback** deterministic top-N + template explanations if API fails or parse yields no valid rows

## API

- `recommend_with_llm(integration, preferences, top_n=5, api_key=None, model=None, timeout_seconds=None, max_retries=3)` → `RecommendationResult`
- `parser.parse_rankings_payload(text, allowed_ids)` → `(rows, error)`
- `fallback.deterministic_rankings(candidates, preferences, top_n)` → `tuple[RankedRecommendation, ...]`

## CLI

From repo root (with `.venv` and Phase 1 deps installed):

```bash
# Live Groq (requires GROQ_API_KEY in environment or .env loaded by your shell)
python -m src.phases.phase4_llm.cli recommend \
  --location Bangalore --budget medium --cuisines Italian \
  --minimum-rating 4.0 --dataset-limit 3000 --top-n 5

# No API: deterministic fallback only (for CI / demos)
python -m src.phases.phase4_llm.cli recommend \
  --location Bangalore --fallback-only --top-n 3 --dataset-limit 500
```

## Dependencies

Phase 4 uses the **stdlib** (`urllib`) for HTTP; no extra pip packages beyond Phase 1 (`datasets` etc.) for the full CLI path.

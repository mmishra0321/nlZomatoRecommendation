# Phase 5: Output Formatting and UX Semantics

Implements `phased-architecture.md` Phase 5:

- **Canonical API DTO:** `RecommendationApiResponse` + `RecommendationItemDTO` + `TelemetryDTO`
- **Formatter:** `build_api_response(integration, result, latency_ms=..., telemetry_extra=...)`
- **Empty / degraded copy:** distinct `user_message` + `detail` + `empty_state_code` (`ok` | `no_filter_match` | `degraded_model`)
- **Markdown:** `format_recommendations_markdown(response)` for demos or copy-to-clipboard

## Usage (Python)

```python
from src.phases.phase3_integration.integration import build_integration_output
from src.phases.phase4_llm.service import recommend_with_llm
from src.phases.phase5_output import build_api_response, recommendation_response_to_json

integration = build_integration_output(restaurants, preferences)
result = recommend_with_llm(integration, preferences, top_n=5)
response = build_api_response(integration, result, latency_ms=elapsed_ms)
print(recommendation_response_to_json(response))
```

## CLI (offline smoke)

```bash
python -m src.phases.phase5_output.cli demo-json
python -m src.phases.phase5_output.cli demo-json --no-candidates
```

Phase 6 (HTTP API) should return `response.to_json_dict()` (or equivalent) as the response body.

# Dataset Contract (V1)

Source dataset: `ManikaSaini/zomato-restaurant-recommendation`  
Purpose: define the canonical fields used by the recommendation pipeline.

## Canonical Restaurant Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Stable internal identifier generated at ingest time. |
| `name` | string | yes | Restaurant name used for display and grounding. |
| `location` | string | yes | Normalized city/locality used for filtering. |
| `cuisines` | list[string] | yes | Normalized cuisine tags for matching. |
| `cost_for_two` | number \| null | no | Numeric estimated cost for two, if available. |
| `budget_band` | enum(`low`,`medium`,`high`,`unknown`) | yes | Derived budget bucket used in filters. |
| `rating` | float | yes | Normalized rating value. |
| `rating_count` | integer \| null | no | Number of ratings/reviews if available. |
| `raw_record` | object | no | Original row snapshot for trace/debug (non-user-facing). |

## Input Normalization Rules
- Trim spaces and normalize case for text fields.
- Split cuisine strings by common separators (`,` `/` `|`) and deduplicate values.
- Coerce ratings to float; reject rows with non-recoverable rating values.
- Parse cost fields to numeric when possible; derive `budget_band` from configured thresholds.
- Create deterministic `id` from normalized `name + location` (plus tie-break suffix if needed).

## Filtering Contract
- Hard filters: `location`, `minimum_rating`, `budget_band`, `cuisine overlap`.
- If user omits `cuisines`, do not apply cuisine hard-filter.
- If `budget` is missing, do not apply budget hard-filter.
- Candidate list must be capped (default: top 30 after deterministic sort).

## Grounding Contract for LLM
- LLM can recommend restaurants only from candidate list.
- Output item must include canonical `id` and `name`.
- Any recommendation not present in candidate list is invalid and removed.

## Validation and Error Handling
- Rows missing `name`, `location`, `rating`, or `cuisines` are dropped.
- Invalid numeric fields are coerced if safe, otherwise set to null or dropped by rule.
- Track and report ingest stats:
  - total rows
  - valid rows
  - dropped rows
  - top drop reasons

## Versioning
- This document defines `dataset_contract_version: v1`.
- Any breaking schema or rule change must bump version and update downstream parser/tests.

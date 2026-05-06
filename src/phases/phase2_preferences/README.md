# Phase 2: User Preferences and Validation

Implements Phase 2 from `phased-architecture.md`:
- structured preference model
- input normalization and validation
- optional allowed-city validation
- CLI command to parse preferences from user input

## Files
- `models.py` - `UserPreferences` dataclass
- `service.py` - parse and validation logic
- `cli.py` - `prefs-parse` command
- `tests/phases/phase2_preferences/test_service.py` - unit tests

## Run CLI
```bash
source .venv/bin/activate
python -m src.phases.phase2_preferences.cli prefs-parse \
  --location Bangalore \
  --budget medium \
  --cuisines Italian Chinese \
  --minimum-rating 4.0 \
  --additional-preferences "family friendly"
```

## Validation Rules
- `location`: required, non-empty
- `budget`: optional, but if provided must be `low|medium|high`
- `cuisines`: optional, deduplicated, max 10
- `minimum_rating`: optional, defaults to `0.0`, must be between `0` and `5`
- `additional_preferences`: optional, max 500 characters

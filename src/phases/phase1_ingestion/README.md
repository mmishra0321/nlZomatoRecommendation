# Phase 1: Data Ingestion and Canonical Model

Implements Phase 1 from `phased-architecture.md`:
- dataset acquisition from Hugging Face
- normalization and canonical schema mapping
- deduplication and drop-reason stats
- smoke CLI for quick verification

## Files
- `models.py` - canonical `Restaurant` schema
- `normalize.py` - parsing and normalization helpers
- `loader.py` - dataset loading and row mapping
- `cli.py` - `ingest-smoke` command

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r src/phases/phase1_ingestion/requirements.txt
```

## Run Smoke Test
```bash
python -m src.phases.phase1_ingestion.cli ingest-smoke --limit 25 --preview 3
```

## Exit Criteria Coverage
- Single module loads and maps dataset into typed objects
- Normalization rules handle ratings, costs, cuisines, text cleanup
- Invalid rows are dropped with explicit reason counts
- Smoke command gives ingestion stats + sample canonical rows

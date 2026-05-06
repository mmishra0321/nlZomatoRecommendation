"""Load repo `.env` into `os.environ` (no extra dependencies)."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path | None = None) -> None:
    root = Path(__file__).resolve().parents[3]
    env_path = path or (root / ".env")
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if value.startswith("<") and value.endswith(">"):
            value = value[1:-1].strip()
        if key and value:
            os.environ[key] = value
    # Aliases if GROQ_API_KEY not set explicitly
    if not os.environ.get("GROQ_API_KEY", "").strip():
        for alias in ("GROK_API_KEY", "zomato_project_API_key", "GROQ_KEY"):
            v = os.environ.get(alias, "").strip()
            if v:
                os.environ["GROQ_API_KEY"] = v
                break

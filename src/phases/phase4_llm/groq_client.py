from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


@dataclass
class GroqChatResult:
    content: str
    raw_response: dict[str, Any] | None = None


class GroqError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _post_json(url: str, payload: dict[str, Any], api_key: str, timeout: float) -> tuple[int, dict[str, Any] | str]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "python-urllib (zomato-rec-demo/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200) or 200
            text = resp.read().decode("utf-8")
            try:
                return status, json.loads(text)
            except json.JSONDecodeError:
                return status, text
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        try:
            parsed = json.loads(err_body)
        except json.JSONDecodeError:
            parsed = err_body
        raise GroqError(f"HTTP {e.code}: {err_body}", status_code=e.code) from e
    except urllib.error.URLError as e:
        raise GroqError(str(e.reason if hasattr(e, "reason") else e)) from e


def chat_completion(
    messages: list[dict[str, str]],
    *,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: float = 25.0,
    max_retries: int = 3,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> GroqChatResult:
    key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        key = os.environ.get("GROK_API_KEY", "").strip()
    if key.startswith("<") and key.endswith(">"):
        key = key[1:-1].strip()
    if not key:
        raise GroqError("GROQ_API_KEY is not set.")

    mdl = (model or os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")).strip()

    payload: dict[str, Any] = {
        "model": mdl,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            status, data = _post_json(GROQ_CHAT_COMPLETIONS_URL, payload, key, timeout_seconds)
            if status >= 400:
                raise GroqError(f"Unexpected status {status}", status_code=status)
            if not isinstance(data, dict):
                raise GroqError("Non-JSON response from Groq.")

            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                raise GroqError("Missing choices in Groq response.")

            message = choices[0].get("message") or {}
            content = message.get("content")
            if content is None:
                raise GroqError("Missing message content in Groq response.")

            return GroqChatResult(content=str(content).strip(), raw_response=data)
        except GroqError as e:
            last_err = e
            code = e.status_code
            if code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                time.sleep(0.5 * (2**attempt))
                continue
            raise
    assert last_err is not None
    raise last_err

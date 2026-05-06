from __future__ import annotations

from src.phases.phase4_llm.parser import extract_json_object, parse_rankings_payload


def test_extract_json_object_plain() -> None:
    data = extract_json_object('{"rankings": [{"restaurant_id": "a", "rank": 1, "explanation": "x"}]}')
    assert data is not None
    assert data["rankings"][0]["restaurant_id"] == "a"


def test_extract_json_object_fenced() -> None:
    text = 'Here is JSON:\n```json\n{"rankings": []}\n```'
    data = extract_json_object(text)
    assert data == {"rankings": []}


def test_parse_rankings_filters_unknown_ids() -> None:
    text = '{"rankings": [{"restaurant_id": "good", "rank": 1, "explanation": "ok"}, {"restaurant_id": "bad", "rank": 2, "explanation": "no"}]}'
    rows, err = parse_rankings_payload(text, {"good"})
    assert err is None
    assert len(rows) == 1
    assert rows[0]["restaurant_id"] == "good"


def test_parse_rankings_missing_key() -> None:
    rows, err = parse_rankings_payload("{}", {"a"})
    assert err is not None
    assert rows == []

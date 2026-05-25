from app.services.llm.json_utils import parse_json_object


def test_parse_plain_json_object():
    assert parse_json_object('{"status":"ok"}') == {"status": "ok"}


def test_parse_fenced_json_object():
    assert parse_json_object('```json\n{"status":"ok"}\n```') == {"status": "ok"}

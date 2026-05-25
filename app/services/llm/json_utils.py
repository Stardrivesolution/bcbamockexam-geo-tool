from __future__ import annotations

import json
import re
from typing import Any


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse a JSON object from model output.

    Models sometimes wrap JSON in Markdown fences. This helper keeps that
    cleanup in one place.
    """

    cleaned = text.strip()
    fenced = JSON_BLOCK_RE.search(cleaned)
    if fenced:
        cleaned = fenced.group(1).strip()

    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("Expected model output to be a JSON object")
    return parsed

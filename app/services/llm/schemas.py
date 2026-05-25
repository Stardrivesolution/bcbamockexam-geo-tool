from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class LlmMessage(BaseModel):
    role: str
    content: str


class LlmRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    response_format: str = "text"


class LlmResponse(BaseModel):
    provider: str
    model: str
    content: str
    parsed_json: Optional[dict[str, Any]] = None
    prompt_version: Optional[str] = None
    raw_metadata: dict[str, Any] = Field(default_factory=dict)

from __future__ import annotations

from typing import Optional

from openai import OpenAI

from app.core.config import Settings
from app.services.llm.json_utils import parse_json_object
from app.services.llm.schemas import LlmRequest, LlmResponse


class LlmNotConfiguredError(RuntimeError):
    pass


class OpenAICompatibleLlmClient:
    """Thin wrapper around any OpenAI-compatible chat completion API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not settings.llm_api_key:
            raise LlmNotConfiguredError("LLM_API_KEY is not configured")
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_seconds,
        )

    def generate_text(
        self,
        request: LlmRequest,
        prompt_version: Optional[str] = None,
    ) -> LlmResponse:
        response = self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        content = response.choices[0].message.content or ""
        return LlmResponse(
            provider=self.settings.llm_provider,
            model=self.settings.llm_model,
            content=content,
            prompt_version=prompt_version,
            raw_metadata={
                "id": response.id,
                "usage": response.usage.model_dump() if response.usage else None,
            },
        )

    def generate_json(
        self,
        request: LlmRequest,
        prompt_version: Optional[str] = None,
    ) -> LlmResponse:
        response = self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        parsed = parse_json_object(content)
        return LlmResponse(
            provider=self.settings.llm_provider,
            model=self.settings.llm_model,
            content=content,
            parsed_json=parsed,
            prompt_version=prompt_version,
            raw_metadata={
                "id": response.id,
                "usage": response.usage.model_dump() if response.usage else None,
            },
        )

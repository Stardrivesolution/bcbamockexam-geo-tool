from __future__ import annotations

from typing import Any, Optional

from pydantic import ValidationError

from app.schemas.geo_gap import GapQuestion
from app.schemas.intent import IntentQuestionSet
from app.schemas.project import ProjectRead
from app.services.intent.prompts import INTENT_GENERATOR_VERSION, SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.services.llm.client import OpenAICompatibleLlmClient
from app.services.llm.schemas import LlmRequest


class LlmIntentGenerator:
    def __init__(self, llm_client: OpenAICompatibleLlmClient) -> None:
        self.llm_client = llm_client

    def generate(
        self,
        target_keyword: str,
        project: Optional[ProjectRead] = None,
        analysis_run_id: Optional[int] = None,
    ) -> IntentQuestionSet:
        response = self.llm_client.generate_json(
            LlmRequest(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=self._user_prompt(target_keyword, project),
                temperature=0.2,
                max_tokens=1800,
                response_format="json",
            ),
            prompt_version=INTENT_GENERATOR_VERSION,
        )
        questions = self._parse_questions(response.parsed_json or {})
        return IntentQuestionSet(
            project_id=project.id if project else None,
            analysis_run_id=analysis_run_id,
            target_keyword=target_keyword,
            generator_version=INTENT_GENERATOR_VERSION,
            questions=questions,
            source="llm",
        )

    def _user_prompt(self, target_keyword: str, project: Optional[ProjectRead]) -> str:
        competitors = "None provided"
        if project and project.competitors:
            competitors = "\n".join(
                f"- {competitor.name} ({competitor.category})"
                for competitor in project.competitors[:8]
            )
        return USER_PROMPT_TEMPLATE.format(
            brand_name=project.brand_name if project else "Unknown",
            domain=project.domain if project else "Unknown",
            language=project.target_language if project else "en",
            region=project.target_region if project else "US",
            target_keyword=target_keyword,
            competitors=competitors,
        )

    def _parse_questions(self, data: dict[str, Any]) -> list[GapQuestion]:
        raw_questions = data.get("questions", [])
        if not isinstance(raw_questions, list):
            raise ValueError("LLM output must contain a questions list")

        questions = []
        for index, item in enumerate(raw_questions, start=1):
            if not isinstance(item, dict):
                continue
            item.setdefault("id", f"q{index:02d}")
            item.setdefault("priority", 1)
            try:
                questions.append(GapQuestion.model_validate(item))
            except ValidationError:
                continue

        if not questions:
            raise ValueError("LLM output did not include valid questions")
        return questions[:30]

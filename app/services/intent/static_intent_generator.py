from __future__ import annotations

from typing import Optional

from app.schemas.intent import IntentQuestionSet
from app.schemas.project import ProjectRead
from app.services.geo_gap.question_bank import QuestionBank


STATIC_INTENT_GENERATOR_VERSION = "intent-generator-static-v0.1"


class StaticIntentGenerator:
    def generate(
        self,
        target_keyword: str,
        project: Optional[ProjectRead] = None,
        analysis_run_id: Optional[int] = None,
    ) -> IntentQuestionSet:
        return IntentQuestionSet(
            project_id=project.id if project else None,
            analysis_run_id=analysis_run_id,
            target_keyword=target_keyword,
            generator_version=STATIC_INTENT_GENERATOR_VERSION,
            questions=QuestionBank().generate(target_keyword),
            source="static",
        )

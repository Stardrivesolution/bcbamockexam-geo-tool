from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import IntentQuestionSetModel
from app.schemas.intent import IntentQuestionSet


class IntentQuestionSetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, result: IntentQuestionSet) -> IntentQuestionSetModel:
        model = IntentQuestionSetModel(
            project_id=result.project_id,
            analysis_run_id=result.analysis_run_id,
            target_keyword=result.target_keyword,
            generator_version=result.generator_version,
            source=result.source,
            questions=[question.model_dump(mode="json") for question in result.questions],
            raw_result=result.model_dump(mode="json"),
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get(self, question_set_id: int) -> Optional[IntentQuestionSetModel]:
        return self.db.get(IntentQuestionSetModel, question_set_id)

    def get_latest_for_run(self, analysis_run_id: int) -> Optional[IntentQuestionSetModel]:
        return (
            self.db.query(IntentQuestionSetModel)
            .filter(IntentQuestionSetModel.analysis_run_id == analysis_run_id)
            .order_by(IntentQuestionSetModel.created_at.desc())
            .first()
        )

    def list_recent(self, limit: int = 20) -> List[IntentQuestionSetModel]:
        return (
            self.db.query(IntentQuestionSetModel)
            .order_by(IntentQuestionSetModel.created_at.desc())
            .limit(limit)
            .all()
        )

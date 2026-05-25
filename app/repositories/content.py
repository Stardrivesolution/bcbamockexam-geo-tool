from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import ContentBrief
from app.schemas.content import ContentBriefResult


class ContentBriefRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, brief: ContentBriefResult) -> ContentBrief:
        title = "Content Brief"
        if brief.title_options:
            title = brief.title_options[0].text
        model = ContentBrief(
            analysis_run_id=brief.analysis_run_id,
            brief_version=brief.brief_version,
            title=title,
            raw_result=brief.model_dump(mode="json"),
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get(self, brief_id: int) -> Optional[ContentBrief]:
        return self.db.get(ContentBrief, brief_id)

    def list_recent(self, limit: int = 20) -> List[ContentBrief]:
        return (
            self.db.query(ContentBrief)
            .order_by(ContentBrief.created_at.desc())
            .limit(limit)
            .all()
        )

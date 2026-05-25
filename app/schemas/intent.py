from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.geo_gap import GapQuestion


class IntentQuestionSet(BaseModel):
    id: Optional[int] = None
    project_id: Optional[int] = None
    analysis_run_id: Optional[int] = None
    target_keyword: str
    generator_version: str
    questions: list[GapQuestion] = Field(default_factory=list)
    source: str = "llm"
    created_at: Optional[datetime] = None

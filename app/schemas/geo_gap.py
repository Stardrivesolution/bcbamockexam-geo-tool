from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GapQuestion(BaseModel):
    id: str
    question: str
    intent: str
    priority: int = 1


class GapCoverageItem(BaseModel):
    question: GapQuestion
    status: str
    coverage_score: float
    evidence: Optional[str] = None
    recommendation: str


class GeoGapAnalysisResult(BaseModel):
    id: Optional[int] = None
    analysis_run_id: int
    analyzer_version: str
    overall_coverage_score: float
    covered_count: int
    partial_count: int
    missing_count: int
    items: list[GapCoverageItem] = Field(default_factory=list)
    missing_questions: list[GapQuestion] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class GeoReadinessIssue(BaseModel):
    category: str
    severity: str
    message: str
    recommendation: str
    evidence: Optional[str] = None


class GeoReadinessSignal(BaseModel):
    name: str
    passed: bool
    points_awarded: float
    points_possible: float
    evidence: Optional[str] = None


class GeoReadinessDimension(BaseModel):
    name: str
    score: float
    points_awarded: float
    points_possible: float
    signals: list[GeoReadinessSignal] = Field(default_factory=list)


class GeoReadinessResult(BaseModel):
    id: Optional[int] = None
    analysis_run_id: int
    scorer_version: str
    overall_score: float
    dimension_scores: dict[str, float]
    dimensions: list[GeoReadinessDimension]
    issues: list[GeoReadinessIssue]
    recommendations: list[str]
    created_at: Optional[datetime] = None
    raw_metrics: dict[str, Any] = Field(default_factory=dict)

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import GeoReadinessAssessment
from app.schemas.geo_readiness import GeoReadinessResult


class GeoReadinessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, result: GeoReadinessResult) -> GeoReadinessAssessment:
        assessment = GeoReadinessAssessment(
            analysis_run_id=result.analysis_run_id,
            scorer_version=result.scorer_version,
            overall_score=round(result.overall_score),
            dimension_scores=result.dimension_scores,
            issues=[issue.model_dump(mode="json") for issue in result.issues],
            recommendations=result.recommendations,
            raw_result=result.model_dump(mode="json"),
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_latest_for_run(
        self,
        analysis_run_id: int,
    ) -> Optional[GeoReadinessAssessment]:
        return (
            self.db.query(GeoReadinessAssessment)
            .filter(GeoReadinessAssessment.analysis_run_id == analysis_run_id)
            .order_by(GeoReadinessAssessment.created_at.desc())
            .first()
        )

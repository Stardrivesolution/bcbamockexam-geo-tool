from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import GeoGapAnalysis
from app.schemas.geo_gap import GeoGapAnalysisResult


class GeoGapRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, result: GeoGapAnalysisResult) -> GeoGapAnalysis:
        gap_analysis = GeoGapAnalysis(
            analysis_run_id=result.analysis_run_id,
            analyzer_version=result.analyzer_version,
            overall_coverage_score=round(result.overall_coverage_score),
            covered_count=result.covered_count,
            partial_count=result.partial_count,
            missing_count=result.missing_count,
            items=[item.model_dump(mode="json") for item in result.items],
            missing_questions=[
                question.model_dump(mode="json") for question in result.missing_questions
            ],
            recommendations=result.recommendations,
            raw_result=result.model_dump(mode="json"),
        )
        self.db.add(gap_analysis)
        self.db.commit()
        self.db.refresh(gap_analysis)
        return gap_analysis

    def get_latest_for_run(self, analysis_run_id: int) -> Optional[GeoGapAnalysis]:
        return (
            self.db.query(GeoGapAnalysis)
            .filter(GeoGapAnalysis.analysis_run_id == analysis_run_id)
            .order_by(GeoGapAnalysis.created_at.desc())
            .first()
        )

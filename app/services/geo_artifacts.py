from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import AnalysisRun
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.geo_gap import GeoGapRepository
from app.repositories.geo_readiness import GeoReadinessRepository
from app.schemas.geo_gap import GeoGapAnalysisResult
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse
from app.services.geo_gap.analyzer import GeoGapAnalyzer
from app.services.geo_readiness.scorer import GeoReadinessScorer


class GeoArtifactService:
    """Loads or creates GEO artifacts linked to an analysis run."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_completed_run(self, analysis_run_id: int) -> Optional[AnalysisRun]:
        run = AnalysisRunRepository(self.db).get(analysis_run_id)
        if not run or run.status != "completed":
            return None
        return run

    def get_analysis(self, run: AnalysisRun) -> AnalyzePageResponse:
        return AnalyzePageResponse.model_validate(run.raw_result)

    def get_or_create_readiness(
        self,
        analysis_run_id: int,
        analysis: AnalyzePageResponse,
    ) -> GeoReadinessResult:
        repo = GeoReadinessRepository(self.db)
        latest = repo.get_latest_for_run(analysis_run_id)
        if latest:
            result = GeoReadinessResult.model_validate(latest.raw_result)
            result.id = latest.id
            result.created_at = latest.created_at
            return result

        result = GeoReadinessScorer().score(
            analysis_run_id=analysis_run_id,
            analysis=analysis,
        )
        saved = repo.save(result)
        result.id = saved.id
        result.created_at = saved.created_at
        return result

    def get_or_create_gap(
        self,
        analysis_run_id: int,
        analysis: AnalyzePageResponse,
        target_keyword: Optional[str],
    ) -> GeoGapAnalysisResult:
        repo = GeoGapRepository(self.db)
        latest = repo.get_latest_for_run(analysis_run_id)
        if latest:
            result = GeoGapAnalysisResult.model_validate(latest.raw_result)
            result.id = latest.id
            result.created_at = latest.created_at
            return result

        result = GeoGapAnalyzer().analyze(
            analysis_run_id=analysis_run_id,
            analysis=analysis,
            target_keyword=target_keyword,
        )
        saved = repo.save(result)
        result.id = saved.id
        result.created_at = saved.created_at
        return result

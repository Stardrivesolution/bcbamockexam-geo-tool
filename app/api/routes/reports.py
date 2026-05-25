from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.geo_gap import GeoGapRepository
from app.repositories.geo_readiness import GeoReadinessRepository
from app.repositories.reports import ReportRepository
from app.schemas.geo_gap import GeoGapAnalysisResult
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse
from app.schemas.report import ReportCreateResponse, ReportSummary
from app.services.geo_gap.analyzer import GeoGapAnalyzer
from app.services.geo_readiness.scorer import GeoReadinessScorer
from app.services.reports.geo_report_builder import GeoReportBuilder

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/geo/{analysis_run_id}", response_model=ReportCreateResponse)
async def create_geo_report(
    analysis_run_id: int,
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    run = AnalysisRunRepository(db).get(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if run.status != "completed":
        raise HTTPException(status_code=409, detail="Analysis run is not completed")

    analysis = AnalyzePageResponse.model_validate(run.raw_result)
    readiness = _get_or_create_readiness(db, analysis_run_id, analysis)
    gap = _get_or_create_gap(db, analysis_run_id, analysis, run.target_keyword)

    report = GeoReportBuilder().build(
        analysis_run_id=analysis_run_id,
        analysis=analysis,
        readiness=readiness,
        gap=gap,
    )
    saved = ReportRepository(db).save(report)
    report.id = saved.id
    report.created_at = saved.created_at
    return report


@router.get("", response_model=list[ReportSummary])
async def list_reports(
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[ReportSummary]:
    return ReportRepository(db).list_recent(limit=min(limit, 100))


@router.get("/{report_id}", response_model=ReportCreateResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    report = ReportRepository(db).get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportCreateResponse(
        id=report.id,
        analysis_run_id=report.analysis_run_id,
        report_type=report.report_type,
        title=report.title,
        format=report.format,
        content=report.content,
        created_at=report.created_at,
    )


def _get_or_create_readiness(
    db: Session,
    analysis_run_id: int,
    analysis: AnalyzePageResponse,
) -> GeoReadinessResult:
    repo = GeoReadinessRepository(db)
    latest = repo.get_latest_for_run(analysis_run_id)
    if latest:
        result = GeoReadinessResult.model_validate(latest.raw_result)
        result.id = latest.id
        result.created_at = latest.created_at
        return result

    result = GeoReadinessScorer().score(analysis_run_id=analysis_run_id, analysis=analysis)
    saved = repo.save(result)
    result.id = saved.id
    result.created_at = saved.created_at
    return result


def _get_or_create_gap(
    db: Session,
    analysis_run_id: int,
    analysis: AnalyzePageResponse,
    target_keyword: Optional[str],
) -> GeoGapAnalysisResult:
    repo = GeoGapRepository(db)
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

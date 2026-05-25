from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.reports import ReportRepository
from app.schemas.report import ReportCreateResponse, ReportSummary
from app.services.geo_artifacts import GeoArtifactService
from app.services.reports.geo_report_builder import GeoReportBuilder

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/geo/{analysis_run_id}", response_model=ReportCreateResponse)
async def create_geo_report(
    analysis_run_id: int,
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    artifacts = GeoArtifactService(db)
    run = artifacts.get_completed_run(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    analysis = artifacts.get_analysis(run)
    readiness = artifacts.get_or_create_readiness(analysis_run_id, analysis)
    gap = artifacts.get_or_create_gap(analysis_run_id, analysis, run.target_keyword)

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

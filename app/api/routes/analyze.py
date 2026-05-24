from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.analysis_runs import AnalysisRunRepository
from app.schemas.page import AnalyzePageRequest, AnalyzePageResponse, AnalysisRunSummary
from app.services.page_analyzer import PageAnalyzer

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/page", response_model=AnalyzePageResponse)
async def analyze_page(
    payload: AnalyzePageRequest,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> AnalyzePageResponse:
    analyzer = PageAnalyzer(settings)
    try:
        result = await analyzer.analyze(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    run = AnalysisRunRepository(db).save_page_analysis(payload, result)
    result.analysis_run_id = run.id
    return result


@router.get("/runs", response_model=list[AnalysisRunSummary])
async def list_analysis_runs(
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[AnalysisRunSummary]:
    runs = AnalysisRunRepository(db).list_recent(limit=min(limit, 100))
    return [
        AnalysisRunSummary(
            id=run.id,
            url=run.page.url,
            final_url=run.page.final_url,
            title=run.page.title,
            target_keyword=run.target_keyword,
            language=run.language,
            status=run.status,
            analyzer_version=run.analyzer_version,
            created_at=run.created_at,
            warnings=run.warnings,
        )
        for run in runs
    ]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.geo_gap import GeoGapRepository
from app.repositories.geo_readiness import GeoReadinessRepository
from app.schemas.geo_gap import GeoGapAnalysisResult
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse
from app.services.geo_gap.analyzer import GeoGapAnalyzer
from app.services.geo_readiness.scorer import GeoReadinessScorer

router = APIRouter(prefix="/geo", tags=["geo"])


@router.post("/readiness/{analysis_run_id}", response_model=GeoReadinessResult)
async def score_geo_readiness(
    analysis_run_id: int,
    db: Session = Depends(get_db),
) -> GeoReadinessResult:
    run = AnalysisRunRepository(db).get(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if run.status != "completed":
        raise HTTPException(status_code=409, detail="Analysis run is not completed")

    analysis = AnalyzePageResponse.model_validate(run.raw_result)
    result = GeoReadinessScorer().score(
        analysis_run_id=analysis_run_id,
        analysis=analysis,
    )

    assessment = GeoReadinessRepository(db).save(result)
    result.id = assessment.id
    result.created_at = assessment.created_at
    return result


@router.post("/gap-analysis/{analysis_run_id}", response_model=GeoGapAnalysisResult)
async def analyze_geo_gaps(
    analysis_run_id: int,
    db: Session = Depends(get_db),
) -> GeoGapAnalysisResult:
    run = AnalysisRunRepository(db).get(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if run.status != "completed":
        raise HTTPException(status_code=409, detail="Analysis run is not completed")

    analysis = AnalyzePageResponse.model_validate(run.raw_result)
    result = GeoGapAnalyzer().analyze(
        analysis_run_id=analysis_run_id,
        analysis=analysis,
        target_keyword=run.target_keyword,
    )

    saved = GeoGapRepository(db).save(result)
    result.id = saved.id
    result.created_at = saved.created_at
    return result

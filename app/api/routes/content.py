from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.content import ContentBriefRepository
from app.schemas.content import ContentBriefResult
from app.services.content.brief_builder import ContentBriefBuilder
from app.services.geo_artifacts import GeoArtifactService

router = APIRouter(prefix="/content", tags=["content"])


@router.post("/brief/{analysis_run_id}", response_model=ContentBriefResult)
async def create_content_brief(
    analysis_run_id: int,
    db: Session = Depends(get_db),
) -> ContentBriefResult:
    artifacts = GeoArtifactService(db)
    run = artifacts.get_completed_run(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    analysis = artifacts.get_analysis(run)
    readiness = artifacts.get_or_create_readiness(analysis_run_id, analysis)
    gap = artifacts.get_or_create_gap(analysis_run_id, analysis, run.target_keyword)

    brief = ContentBriefBuilder().build(
        analysis_run_id=analysis_run_id,
        analysis=analysis,
        readiness=readiness,
        gap=gap,
        target_keyword=run.target_keyword,
    )
    saved = ContentBriefRepository(db).save(brief)
    brief.id = saved.id
    brief.created_at = saved.created_at
    return brief


@router.get("/{brief_id}", response_model=ContentBriefResult)
async def get_content_brief(
    brief_id: int,
    db: Session = Depends(get_db),
) -> ContentBriefResult:
    brief = ContentBriefRepository(db).get(brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Content brief not found")
    result = ContentBriefResult.model_validate(brief.raw_result)
    result.id = brief.id
    result.created_at = brief.created_at
    return result

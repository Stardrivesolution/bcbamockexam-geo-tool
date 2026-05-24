from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.schemas.page import AnalyzePageRequest, AnalyzePageResponse
from app.services.page_analyzer import PageAnalyzer

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("/page", response_model=AnalyzePageResponse)
async def analyze_page(
    payload: AnalyzePageRequest,
    settings: Settings = Depends(get_settings),
) -> AnalyzePageResponse:
    analyzer = PageAnalyzer(settings)
    try:
        return await analyzer.analyze(payload.url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

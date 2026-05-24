from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import AnalysisRun, Page
from app.schemas.page import AnalyzePageRequest, AnalyzePageResponse


class AnalysisRunRepository:
    """Persistence layer for page analysis results.

    Keeping database writes here prevents API routes and service logic from
    becoming tangled with SQL details.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def save_page_analysis(
        self,
        request: AnalyzePageRequest,
        response: AnalyzePageResponse,
    ) -> AnalysisRun:
        page_data = response.page
        page = Page(
            url=request.url,
            final_url=response.crawl.final_url,
            title=page_data.title,
            meta_description=page_data.meta_description,
            h1_count=page_data.h1_count,
            word_count=page_data.word_count,
            has_noindex=page_data.technical.has_noindex,
        )
        self.db.add(page)
        self.db.flush()

        run = AnalysisRun(
            page_id=page.id,
            target_keyword=request.target_keyword,
            language=request.language,
            raw_result=response.model_dump(mode="json"),
            warnings=response.warnings,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get(self, run_id: int) -> Optional[AnalysisRun]:
        return self.db.get(AnalysisRun, run_id)

    def list_recent(self, limit: int = 20) -> List[AnalysisRun]:
        return (
            self.db.query(AnalysisRun)
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
            .all()
        )

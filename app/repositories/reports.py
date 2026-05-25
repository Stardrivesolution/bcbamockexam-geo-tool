from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import GeoReport
from app.schemas.report import ReportCreateResponse


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, report: ReportCreateResponse) -> GeoReport:
        model = GeoReport(
            analysis_run_id=report.analysis_run_id,
            report_type=report.report_type,
            title=report.title,
            format=report.format,
            content=report.content,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def get(self, report_id: int) -> Optional[GeoReport]:
        return self.db.get(GeoReport, report_id)

    def list_recent(self, limit: int = 20) -> List[GeoReport]:
        return (
            self.db.query(GeoReport)
            .order_by(GeoReport.created_at.desc())
            .limit(limit)
            .all()
        )

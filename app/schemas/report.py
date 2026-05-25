from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportCreateResponse(BaseModel):
    id: Optional[int] = None
    analysis_run_id: int
    report_type: str
    title: str
    format: str = "markdown"
    content: str
    created_at: Optional[datetime] = None


class ReportSummary(BaseModel):
    id: int
    analysis_run_id: int
    report_type: str
    title: str
    format: str
    created_at: datetime

    model_config = {"from_attributes": True}

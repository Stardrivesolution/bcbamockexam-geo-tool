from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Competitor(BaseModel):
    name: str
    domain: str
    url: str
    category: str = Field(
        default="direct",
        description="direct, broad, marketplace, content, or unknown",
    )
    notes: Optional[str] = None
    source_url: Optional[str] = None


class ProjectCreate(BaseModel):
    name: str
    brand_name: Optional[str] = None
    domain: Optional[str] = None
    target_language: str = "en"
    target_region: Optional[str] = "US"
    competitors: List[Competitor] = Field(default_factory=list)
    project_metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectRead(BaseModel):
    id: int
    name: str
    brand_name: Optional[str] = None
    domain: Optional[str] = None
    target_language: str
    target_region: Optional[str] = None
    competitors: List[Competitor] = Field(default_factory=list)
    project_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}

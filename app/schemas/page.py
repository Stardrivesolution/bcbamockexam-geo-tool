from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, HttpUrl


class AnalyzePageRequest(BaseModel):
    url: str = Field(..., description="Page URL to analyze")
    project_id: Optional[int] = Field(
        default=None,
        description="Optional project id used to associate this analysis with a brand/site",
    )
    target_keyword: Optional[str] = Field(
        default=None,
        description="Optional keyword/topic used later by GEO scoring agents",
    )
    language: str = Field(default="zh-CN")


class Heading(BaseModel):
    level: int
    text: str


class LinkItem(BaseModel):
    text: str
    href: str
    is_internal: bool


class ImageItem(BaseModel):
    src: str
    alt: Optional[str] = None


class CrawlMetadata(BaseModel):
    final_url: str
    status_code: int
    content_type: Optional[str] = None
    fetched_at: datetime
    elapsed_ms: int


class TechnicalSignals(BaseModel):
    canonical_url: Optional[str] = None
    meta_robots: Optional[str] = None
    has_noindex: bool = False
    robots_txt_url: Optional[str] = None
    robots_txt_status_code: Optional[int] = None


class ContentStructure(BaseModel):
    list_count: int = 0
    table_count: int = 0
    faq_heading_count: int = 0
    question_mark_count: int = 0


class ExtractedPage(BaseModel):
    url: str
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_count: int
    headings: list[Heading]
    main_text: str
    word_count: int
    links: list[LinkItem]
    images: list[ImageItem]
    json_ld: list[dict[str, Any]]
    technical: TechnicalSignals
    structure: ContentStructure = Field(default_factory=ContentStructure)


class AnalyzePageResponse(BaseModel):
    analysis_run_id: Optional[int] = None
    crawl: CrawlMetadata
    page: ExtractedPage
    warnings: list[str] = Field(default_factory=list)


class AnalysisRunSummary(BaseModel):
    id: int
    url: str
    final_url: str
    title: Optional[str] = None
    target_keyword: Optional[str] = None
    language: str
    status: str
    analyzer_version: str
    created_at: datetime
    warnings: list[str] = Field(default_factory=list)

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TitleDraft(BaseModel):
    text: str
    rationale: str


class MetaDescriptionDraft(BaseModel):
    text: str
    rationale: str


class FaqDraft(BaseModel):
    question: str
    answer_angle: str
    source_gap_status: str


class SectionDraft(BaseModel):
    heading: str
    purpose: str
    talking_points: list[str] = Field(default_factory=list)


class SchemaDraft(BaseModel):
    schema_type: str
    purpose: str
    required_fields: list[str] = Field(default_factory=list)


class ContentBriefResult(BaseModel):
    id: Optional[int] = None
    analysis_run_id: int
    brief_version: str
    title_options: list[TitleDraft] = Field(default_factory=list)
    meta_description_options: list[MetaDescriptionDraft] = Field(default_factory=list)
    direct_answer_block: str
    faq_drafts: list[FaqDraft] = Field(default_factory=list)
    section_drafts: list[SectionDraft] = Field(default_factory=list)
    schema_drafts: list[SchemaDraft] = Field(default_factory=list)
    editorial_notes: list[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

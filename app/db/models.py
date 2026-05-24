from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    competitors: Mapped[List] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    pages: Mapped[List["Page"]] = relationship(back_populates="project")
    analysis_runs: Mapped[List["AnalysisRun"]] = relationship(back_populates="project")


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    final_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h1_count: Mapped[int] = mapped_column(Integer, default=0)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    has_noindex: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    project: Mapped[Optional["Project"]] = relationship(back_populates="pages")
    analysis_runs: Mapped[List["AnalysisRun"]] = relationship(back_populates="page")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id"), nullable=False)
    run_type: Mapped[str] = mapped_column(String(80), default="page_analysis")
    status: Mapped[str] = mapped_column(String(50), default="completed")
    target_keyword: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="zh-CN")
    analyzer_version: Mapped[str] = mapped_column(String(50), default="page-analysis-v0.1")
    raw_result: Mapped[dict] = mapped_column(JSON, default=dict)
    warnings: Mapped[List] = mapped_column(JSON, default=list)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    project: Mapped[Optional["Project"]] = relationship(back_populates="analysis_runs")
    page: Mapped["Page"] = relationship(back_populates="analysis_runs")

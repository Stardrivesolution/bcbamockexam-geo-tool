from datetime import datetime, timezone

from app.schemas.geo_gap import GapCoverageItem, GapQuestion, GeoGapAnalysisResult
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse, CrawlMetadata, ExtractedPage, TechnicalSignals
from app.services.content.brief_builder import ContentBriefBuilder


def test_content_brief_builder_uses_gap_questions():
    analysis = AnalyzePageResponse(
        analysis_run_id=1,
        crawl=CrawlMetadata(
            final_url="https://example.com",
            status_code=200,
            fetched_at=datetime.now(timezone.utc),
            elapsed_ms=10,
        ),
        page=ExtractedPage(
            url="https://example.com",
            title="BCBA Mock Exam",
            meta_description="Practice for your exam.",
            h1_count=1,
            headings=[],
            main_text="Sample content.",
            word_count=20,
            links=[],
            images=[],
            json_ld=[],
            technical=TechnicalSignals(),
        ),
    )
    readiness = GeoReadinessResult(
        analysis_run_id=1,
        scorer_version="test",
        overall_score=80,
        dimension_scores={"schema": 50},
        dimensions=[],
        issues=[],
        recommendations=[],
    )
    gap = GeoGapAnalysisResult(
        analysis_run_id=1,
        analyzer_version="test",
        overall_coverage_score=50,
        covered_count=0,
        partial_count=0,
        missing_count=1,
        items=[
            GapCoverageItem(
                question=GapQuestion(id="q1", question="How is it scored?", intent="scoring"),
                status="missing",
                coverage_score=0,
                recommendation="Add scoring.",
            )
        ],
        missing_questions=[],
        recommendations=[],
    )

    brief = ContentBriefBuilder().build(1, analysis, readiness, gap, "BCBA mock exam")

    assert brief.title_options
    assert "BCBA Mock Exam" in brief.title_options[0].text
    assert "BCBA Mock Exam" in brief.direct_answer_block
    assert brief.faq_drafts[0].question == "How is it scored?"
    assert any(section.heading == "How Scoring and Review Work" for section in brief.section_drafts)

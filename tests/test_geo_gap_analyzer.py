from datetime import datetime, timezone

from app.schemas.page import AnalyzePageResponse, CrawlMetadata, ExtractedPage, TechnicalSignals
from app.services.geo_gap.analyzer import GeoGapAnalyzer


def test_geo_gap_analysis_detects_missing_questions():
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
            main_text="Our BCBA mock exam includes practice questions and answer explanations.",
            word_count=10,
            links=[],
            images=[],
            json_ld=[],
            technical=TechnicalSignals(),
        ),
    )

    result = GeoGapAnalyzer().analyze(
        analysis_run_id=1,
        analysis=analysis,
        target_keyword="BCBA mock exam",
    )

    assert result.overall_coverage_score < 70
    assert result.missing_count > 0
    assert any(item.question.intent == "pricing" for item in result.items)

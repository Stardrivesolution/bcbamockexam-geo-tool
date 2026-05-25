from datetime import datetime, timezone

from app.schemas.geo_gap import GapCoverageItem, GapQuestion, GeoGapAnalysisResult
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse, CrawlMetadata, ExtractedPage, TechnicalSignals
from app.services.reports.geo_report_builder import GeoReportBuilder


def test_geo_report_builder_includes_scores_and_gaps():
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
        dimension_scores={"metadata": 100},
        dimensions=[],
        issues=[],
        recommendations=["Add FAQ schema."],
    )
    gap = GeoGapAnalysisResult(
        analysis_run_id=1,
        analyzer_version="test",
        overall_coverage_score=50,
        covered_count=1,
        partial_count=1,
        missing_count=1,
        items=[
            GapCoverageItem(
                question=GapQuestion(id="q1", question="How is it scored?", intent="scoring"),
                status="missing",
                coverage_score=0,
                recommendation="Add a clear answer for scoring.",
            )
        ],
        recommendations=["Strengthen scoring coverage."],
    )

    report = GeoReportBuilder().build(1, analysis, readiness, gap)

    assert "GEO Readiness Score: 80" in report.content
    assert "Gap Coverage Score: 50" in report.content
    assert "How is it scored?" in report.content

from datetime import datetime, timezone

from app.schemas.page import AnalyzePageResponse, CrawlMetadata, ExtractedPage, TechnicalSignals
from app.services.geo_readiness.scorer import GeoReadinessScorer


def test_geo_readiness_flags_missing_basics():
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
            title=None,
            meta_description=None,
            h1_count=0,
            headings=[],
            main_text="Short page.",
            word_count=2,
            links=[],
            images=[],
            json_ld=[],
            technical=TechnicalSignals(),
        ),
    )

    result = GeoReadinessScorer().score(analysis_run_id=1, analysis=analysis)

    assert result.overall_score < 40
    assert any(issue.message == "Missing page title." for issue in result.issues)
    assert any(issue.message == "Missing meta description." for issue in result.issues)

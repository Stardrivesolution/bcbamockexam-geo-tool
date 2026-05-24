from __future__ import annotations

import httpx

from app.core.config import Settings
from app.schemas.page import AnalyzePageResponse, CrawlMetadata
from app.services.crawler import PageCrawler
from app.services.extractor import HtmlExtractor
from app.utils.urls import normalize_url


class PageAnalyzer:
    """Application service for the first MVP workflow: URL -> page data."""

    def __init__(self, settings: Settings) -> None:
        self.crawler = PageCrawler(settings)
        self.extractor = HtmlExtractor()

    async def analyze(self, raw_url: str) -> AnalyzePageResponse:
        warnings: list[str] = []
        url = normalize_url(raw_url)

        try:
            crawl = await self.crawler.fetch(url)
        except httpx.HTTPStatusError as exc:
            raise ValueError(f"Page returned HTTP {exc.response.status_code}") from exc
        except httpx.HTTPError as exc:
            raise ValueError(f"Failed to fetch page: {exc}") from exc

        page = self.extractor.extract(crawl.html, crawl.final_url)
        page.technical.robots_txt_url = crawl.robots_txt_url
        page.technical.robots_txt_status_code = crawl.robots_txt_status_code

        if page.h1_count != 1:
            warnings.append(f"Expected exactly one H1, found {page.h1_count}.")
        if not page.title:
            warnings.append("Missing page title.")
        if not page.meta_description:
            warnings.append("Missing meta description.")
        if page.technical.has_noindex:
            warnings.append("Page contains noindex; AI/search visibility will be limited.")

        return AnalyzePageResponse(
            crawl=CrawlMetadata(
                final_url=crawl.final_url,
                status_code=crawl.status_code,
                content_type=crawl.content_type,
                fetched_at=crawl.fetched_at,
                elapsed_ms=crawl.elapsed_ms,
            ),
            page=page,
            warnings=warnings,
        )

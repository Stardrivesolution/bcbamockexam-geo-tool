from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Optional

import httpx

from app.core.config import Settings
from app.utils.urls import get_origin


@dataclass(frozen=True)
class CrawlResult:
    requested_url: str
    final_url: str
    status_code: int
    content_type: Optional[str]
    html: str
    fetched_at: datetime
    elapsed_ms: int
    robots_txt_url: str
    robots_txt_status_code: Optional[int]


class PageCrawler:
    """Fetches page HTML and lightweight robots metadata.

    This is deliberately deterministic. Agent logic should consume the
    structured result rather than trying to browse pages itself.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch(self, url: str) -> CrawlResult:
        timeout = httpx.Timeout(self.settings.http_timeout_seconds)
        headers = {
            "User-Agent": (
                "GEOInternalTool/0.1 "
                "(company-internal analysis; compatible; +https://example.com)"
            )
        }

        started = perf_counter()
        async with httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            elapsed_ms = round((perf_counter() - started) * 1000)
            response.raise_for_status()

            content = response.content[: self.settings.max_html_bytes]
            html = content.decode(response.encoding or "utf-8", errors="replace")

            robots_url = f"{get_origin(str(response.url))}/robots.txt"
            robots_status: Optional[int]
            try:
                robots_response = await client.get(robots_url)
                robots_status = robots_response.status_code
            except httpx.HTTPError:
                robots_status = None

        return CrawlResult(
            requested_url=url,
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("content-type"),
            html=html,
            fetched_at=datetime.now(timezone.utc),
            elapsed_ms=elapsed_ms,
            robots_txt_url=robots_url,
            robots_txt_status_code=robots_status,
        )

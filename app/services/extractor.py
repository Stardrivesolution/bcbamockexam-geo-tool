from __future__ import annotations

import json
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.schemas.page import ExtractedPage, Heading, ImageItem, LinkItem, TechnicalSignals


WHITESPACE_RE = re.compile(r"\s+")


class HtmlExtractor:
    """Turns raw HTML into the stable page data used by later GEO agents."""

    def extract(self, html: str, final_url: str) -> ExtractedPage:
        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "noscript", "template", "svg"]):
            tag.decompose()

        title = self._clean_text(soup.title.get_text(" ")) if soup.title else None
        meta_description = self._meta_content(soup, "description")
        meta_robots = self._meta_content(soup, "robots")
        canonical_url = self._canonical(soup, final_url)

        headings = self._extract_headings(soup)
        links = self._extract_links(soup, final_url)
        images = self._extract_images(soup, final_url)
        json_ld = self._extract_json_ld(html)
        main_text = self._extract_main_text(soup)

        return ExtractedPage(
            url=final_url,
            title=title,
            meta_description=meta_description,
            h1_count=sum(1 for heading in headings if heading.level == 1),
            headings=headings,
            main_text=main_text,
            word_count=self._count_words(main_text),
            links=links,
            images=images,
            json_ld=json_ld,
            technical=TechnicalSignals(
                canonical_url=canonical_url,
                meta_robots=meta_robots,
                has_noindex="noindex" in (meta_robots or "").lower(),
            ),
        )

    def _meta_content(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        tag = soup.find("meta", attrs={"name": re.compile(f"^{name}$", re.I)})
        if not tag:
            return None
        return self._clean_text(tag.get("content", ""))

    def _canonical(self, soup: BeautifulSoup, final_url: str) -> Optional[str]:
        tag = soup.find("link", rel=lambda value: value and "canonical" in value)
        href = tag.get("href") if tag else None
        return urljoin(final_url, href) if href else None

    def _extract_headings(self, soup: BeautifulSoup) -> list[Heading]:
        headings: list[Heading] = []
        for tag in soup.find_all(re.compile("^h[1-6]$")):
            text = self._clean_text(tag.get_text(" "))
            if text:
                headings.append(Heading(level=int(tag.name[1]), text=text))
        return headings

    def _extract_links(self, soup: BeautifulSoup, final_url: str) -> list[LinkItem]:
        base_domain = urlparse(final_url).netloc
        links: list[LinkItem] = []
        for tag in soup.find_all("a", href=True):
            href = urljoin(final_url, tag["href"])
            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"}:
                continue
            text = self._clean_text(tag.get_text(" "))
            links.append(
                LinkItem(
                    text=text[:160],
                    href=href,
                    is_internal=parsed.netloc == base_domain,
                )
            )
        return links

    def _extract_images(self, soup: BeautifulSoup, final_url: str) -> list[ImageItem]:
        images: list[ImageItem] = []
        for tag in soup.find_all("img"):
            src = tag.get("src") or tag.get("data-src")
            if not src:
                continue
            alt = self._clean_text(tag.get("alt", "")) or None
            images.append(ImageItem(src=urljoin(final_url, src), alt=alt))
        return images

    def _extract_json_ld(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        items: list[dict] = []
        for tag in soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.I)}):
            raw = tag.string or tag.get_text()
            if not raw:
                continue
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                items.append(parsed)
            elif isinstance(parsed, list):
                items.extend(item for item in parsed if isinstance(item, dict))
        return items

    def _extract_main_text(self, soup: BeautifulSoup) -> str:
        candidate = soup.find("main") or soup.find("article") or soup.body or soup
        text = candidate.get_text(" ")
        return self._clean_text(text)

    def _clean_text(self, text: str) -> str:
        return WHITESPACE_RE.sub(" ", text).strip()

    def _count_words(self, text: str) -> int:
        # Chinese pages often do not use spaces, so count CJK characters as units.
        cjk_chars = re.findall(r"[\u4e00-\u9fff]", text)
        latin_words = re.findall(r"[A-Za-z0-9]+(?:[-_'][A-Za-z0-9]+)?", text)
        return len(cjk_chars) + len(latin_words)

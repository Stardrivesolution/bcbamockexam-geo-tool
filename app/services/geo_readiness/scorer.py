from __future__ import annotations

from typing import Optional

from app.schemas.geo_readiness import (
    GeoReadinessDimension,
    GeoReadinessIssue,
    GeoReadinessResult,
    GeoReadinessSignal,
)
from app.schemas.page import AnalyzePageResponse, ExtractedPage


SCORER_VERSION = "geo-readiness-rules-v0.1"


class GeoReadinessScorer:
    """Rule-based first pass for GEO readiness.

    This scorer is intentionally deterministic. LLM-based semantic scoring can
    be added later as another scorer version without breaking this baseline.
    """

    def score(
        self,
        analysis_run_id: int,
        analysis: AnalyzePageResponse,
    ) -> GeoReadinessResult:
        page = analysis.page
        dimensions = [
            self._metadata(page),
            self._crawlability(page),
            self._structure(page),
            self._content_depth(page),
            self._schema(page),
            self._links(page),
            self._media(page),
        ]

        issues: list[GeoReadinessIssue] = []
        recommendations: list[str] = []
        for dimension in dimensions:
            for signal in dimension.signals:
                if not signal.passed:
                    issue = self._issue_for_signal(dimension.name, signal)
                    issues.append(issue)
                    recommendations.append(issue.recommendation)

        points_awarded = sum(d.points_awarded for d in dimensions)
        points_possible = sum(d.points_possible for d in dimensions)
        overall_score = self._score(points_awarded, points_possible)

        return GeoReadinessResult(
            analysis_run_id=analysis_run_id,
            scorer_version=SCORER_VERSION,
            overall_score=overall_score,
            dimension_scores={dimension.name: dimension.score for dimension in dimensions},
            dimensions=dimensions,
            issues=issues,
            recommendations=self._dedupe(recommendations),
            raw_metrics={
                "word_count": page.word_count,
                "h1_count": page.h1_count,
                "internal_links": sum(1 for link in page.links if link.is_internal),
                "external_links": sum(1 for link in page.links if not link.is_internal),
                "image_count": len(page.images),
                "images_with_alt": sum(1 for image in page.images if image.alt),
                "json_ld_count": len(page.json_ld),
                "list_count": page.structure.list_count,
                "table_count": page.structure.table_count,
                "faq_heading_count": page.structure.faq_heading_count,
                "question_mark_count": page.structure.question_mark_count,
            },
        )

    def _metadata(self, page: ExtractedPage) -> GeoReadinessDimension:
        title_len = len(page.title or "")
        meta_len = len(page.meta_description or "")
        signals = [
            self._signal("title_present", bool(page.title), 6, page.title),
            self._signal("title_length_reasonable", 20 <= title_len <= 70, 4, f"{title_len} chars"),
            self._signal("meta_description_present", bool(page.meta_description), 6, page.meta_description),
            self._signal("meta_description_length_reasonable", 80 <= meta_len <= 170, 4, f"{meta_len} chars"),
        ]
        return self._dimension("metadata", signals)

    def _crawlability(self, page: ExtractedPage) -> GeoReadinessDimension:
        signals = [
            self._signal("not_noindex", not page.technical.has_noindex, 8, page.technical.meta_robots),
            self._signal("canonical_present", bool(page.technical.canonical_url), 4, page.technical.canonical_url),
            self._signal(
                "robots_txt_checked",
                page.technical.robots_txt_status_code in {200, 404},
                3,
                str(page.technical.robots_txt_status_code),
            ),
        ]
        return self._dimension("crawlability", signals)

    def _structure(self, page: ExtractedPage) -> GeoReadinessDimension:
        heading_levels = [heading.level for heading in page.headings]
        has_supporting_headings = any(level in {2, 3} for level in heading_levels)
        has_qa_structure = (
            page.structure.faq_heading_count > 0 or page.structure.question_mark_count >= 3
        )
        signals = [
            self._signal("single_h1", page.h1_count == 1, 6, f"{page.h1_count} H1 tags"),
            self._signal("supporting_headings", has_supporting_headings, 5, f"{len(page.headings)} headings"),
            self._signal("lists_or_tables_present", page.structure.list_count + page.structure.table_count > 0, 4),
            self._signal("faq_or_question_structure", has_qa_structure, 5),
        ]
        return self._dimension("structure", signals)

    def _content_depth(self, page: ExtractedPage) -> GeoReadinessDimension:
        has_direct_answer_candidate = self._has_direct_answer_candidate(page.main_text)
        signals = [
            self._signal("enough_text", page.word_count >= 600, 8, f"{page.word_count} word units"),
            self._signal("substantial_text", page.word_count >= 1200, 4, f"{page.word_count} word units"),
            self._signal("direct_answer_candidate", has_direct_answer_candidate, 5),
            self._signal("question_coverage_signals", page.structure.question_mark_count >= 3, 3),
        ]
        return self._dimension("content", signals)

    def _schema(self, page: ExtractedPage) -> GeoReadinessDimension:
        schema_types = self._schema_types(page)
        useful_types = {"Organization", "WebSite", "Article", "FAQPage", "Product", "Service", "BreadcrumbList"}
        signals = [
            self._signal("json_ld_present", len(page.json_ld) > 0, 8, f"{len(page.json_ld)} JSON-LD blocks"),
            self._signal("useful_schema_type", bool(schema_types & useful_types), 7, ", ".join(sorted(schema_types))),
        ]
        return self._dimension("schema", signals)

    def _links(self, page: ExtractedPage) -> GeoReadinessDimension:
        internal_count = sum(1 for link in page.links if link.is_internal)
        external_count = sum(1 for link in page.links if not link.is_internal)
        signals = [
            self._signal("internal_links_present", internal_count >= 3, 5, f"{internal_count} internal links"),
            self._signal("external_or_reference_links_present", external_count >= 1, 5, f"{external_count} external links"),
        ]
        return self._dimension("links", signals)

    def _media(self, page: ExtractedPage) -> GeoReadinessDimension:
        if not page.images:
            signals = [
                self._signal("images_present", False, 4, "0 images"),
                self._signal("image_alt_coverage", False, 6, "0% alt coverage"),
            ]
            return self._dimension("media", signals)

        images_with_alt = sum(1 for image in page.images if image.alt)
        alt_ratio = images_with_alt / len(page.images)
        signals = [
            self._signal("images_present", True, 4, f"{len(page.images)} images"),
            self._signal("image_alt_coverage", alt_ratio >= 0.8, 6, f"{alt_ratio:.0%} alt coverage"),
        ]
        return self._dimension("media", signals)

    def _signal(
        self,
        name: str,
        passed: bool,
        points: float,
        evidence: Optional[str] = None,
    ) -> GeoReadinessSignal:
        return GeoReadinessSignal(
            name=name,
            passed=passed,
            points_awarded=points if passed else 0,
            points_possible=points,
            evidence=evidence,
        )

    def _dimension(
        self,
        name: str,
        signals: list[GeoReadinessSignal],
    ) -> GeoReadinessDimension:
        points_awarded = sum(signal.points_awarded for signal in signals)
        points_possible = sum(signal.points_possible for signal in signals)
        return GeoReadinessDimension(
            name=name,
            score=self._score(points_awarded, points_possible),
            points_awarded=points_awarded,
            points_possible=points_possible,
            signals=signals,
        )

    def _score(self, awarded: float, possible: float) -> float:
        if possible <= 0:
            return 0
        return round((awarded / possible) * 100, 2)

    def _issue_for_signal(
        self,
        category: str,
        signal: GeoReadinessSignal,
    ) -> GeoReadinessIssue:
        messages = {
            "title_present": ("Missing page title.", "Add a clear, keyword-relevant title tag."),
            "title_length_reasonable": ("Title length is outside the recommended range.", "Keep the title roughly 20-70 characters."),
            "meta_description_present": ("Missing meta description.", "Add a concise meta description that states the page value clearly."),
            "meta_description_length_reasonable": ("Meta description length is not ideal.", "Aim for an 80-170 character meta description."),
            "not_noindex": ("Page has a noindex signal.", "Remove noindex if this page should be discoverable by search and AI systems."),
            "canonical_present": ("Missing canonical URL.", "Add a canonical URL to clarify the preferred page version."),
            "robots_txt_checked": ("robots.txt could not be checked.", "Confirm robots.txt is reachable or intentionally absent."),
            "single_h1": ("Page should have exactly one H1.", "Use one clear H1 that states the page topic."),
            "supporting_headings": ("Page lacks supporting H2/H3 headings.", "Add descriptive H2/H3 sections for major user questions."),
            "lists_or_tables_present": ("Page lacks lists or tables.", "Add steps, checklists, comparison tables, or feature lists where useful."),
            "faq_or_question_structure": ("Page lacks FAQ or question-style structure.", "Add FAQ sections based on real user questions."),
            "enough_text": ("Page content appears thin.", "Expand the page with useful explanations, examples, and direct answers."),
            "substantial_text": ("Page may need more topical depth.", "Add deeper coverage of exam format, practice strategy, scoring, and examples."),
            "direct_answer_candidate": ("No obvious direct-answer block found.", "Add a short answer block that directly explains what the page offers and who it helps."),
            "question_coverage_signals": ("Few question-style signals found.", "Add more user-centered questions and answers."),
            "json_ld_present": ("No JSON-LD structured data found.", "Add relevant JSON-LD such as Organization, WebSite, Product, Service, or FAQPage."),
            "useful_schema_type": ("JSON-LD lacks useful GEO/SEO schema types.", "Use schema types that match the visible page content."),
            "internal_links_present": ("Few internal links found.", "Add internal links to related study guides, mock exams, pricing, and FAQ pages."),
            "external_or_reference_links_present": ("No external/reference links found.", "Add trustworthy references where they help validate claims."),
            "images_present": ("No images found.", "Add meaningful visuals only if they help explain the product or study process."),
            "image_alt_coverage": ("Image alt coverage is low.", "Add descriptive alt text to important images."),
        }
        message, recommendation = messages.get(
            signal.name,
            ("Readiness signal failed.", "Review this signal and improve the page."),
        )
        severity = "high" if signal.points_possible >= 6 else "medium"
        return GeoReadinessIssue(
            category=category,
            severity=severity,
            message=message,
            recommendation=recommendation,
            evidence=signal.evidence,
        )

    def _schema_types(self, page: ExtractedPage) -> set[str]:
        types: set[str] = set()
        for item in page.json_ld:
            raw_type = item.get("@type")
            if isinstance(raw_type, str):
                types.add(raw_type)
            elif isinstance(raw_type, list):
                types.update(value for value in raw_type if isinstance(value, str))
            graph = item.get("@graph")
            if isinstance(graph, list):
                for graph_item in graph:
                    if isinstance(graph_item, dict) and isinstance(graph_item.get("@type"), str):
                        types.add(graph_item["@type"])
        return types

    def _has_direct_answer_candidate(self, text: str) -> bool:
        lower_text = text.lower()
        answer_patterns = [
            "is a",
            "is an",
            "helps",
            "includes",
            "designed to",
            "bcba mock exam",
            "practice exam",
        ]
        return any(pattern in lower_text for pattern in answer_patterns)

    def _dedupe(self, values: list[str]) -> list[str]:
        seen = set()
        deduped = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        return deduped

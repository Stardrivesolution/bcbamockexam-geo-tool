from __future__ import annotations

from typing import Optional

from app.schemas.content import (
    ContentBriefResult,
    FaqDraft,
    MetaDescriptionDraft,
    SchemaDraft,
    SectionDraft,
    TitleDraft,
)
from app.schemas.geo_gap import GeoGapAnalysisResult, GapCoverageItem
from app.schemas.geo_readiness import GeoReadinessResult
from app.schemas.page import AnalyzePageResponse


BRIEF_VERSION = "content-brief-rules-v0.1"


class ContentBriefBuilder:
    """Creates a human-reviewable content brief from GEO findings."""

    def build(
        self,
        analysis_run_id: int,
        analysis: AnalyzePageResponse,
        readiness: GeoReadinessResult,
        gap: GeoGapAnalysisResult,
        target_keyword: Optional[str],
    ) -> ContentBriefResult:
        topic = target_keyword or "BCBA mock exam"
        page = analysis.page
        weak_items = [
            item for item in gap.items if item.status in {"partial", "missing"}
        ]

        return ContentBriefResult(
            analysis_run_id=analysis_run_id,
            brief_version=BRIEF_VERSION,
            title_options=self._title_options(topic),
            meta_description_options=self._meta_options(topic),
            direct_answer_block=self._direct_answer_block(topic),
            faq_drafts=self._faq_drafts(weak_items),
            section_drafts=self._section_drafts(weak_items),
            schema_drafts=self._schema_drafts(readiness, gap),
            editorial_notes=self._editorial_notes(page.word_count),
        )

    def _title_options(self, topic: str) -> list[TitleDraft]:
        display_topic = self._display_topic(topic)
        return [
            TitleDraft(
                text=f"{display_topic} | Online Practice Test & Study Guide",
                rationale="Combines the target topic with the product type and study intent.",
            ),
            TitleDraft(
                text="BCBA Mock Exam: Practice Questions, Answers & Prep Guide",
                rationale="Highlights practice questions, answers, and exam-prep value.",
            ),
            TitleDraft(
                text="BCBA Exam Prep Mock Test With Answer Review",
                rationale="Targets users looking for exam prep and post-test review.",
            ),
        ]

    def _meta_options(self, topic: str) -> list[MetaDescriptionDraft]:
        display_topic = self._display_topic(topic)
        return [
            MetaDescriptionDraft(
                text=(
                    f"Prepare with a {display_topic} designed for BCBA candidates. "
                    "Review practice questions, answer explanations, and study guidance."
                ),
                rationale="Directly states audience, product, and learning benefit.",
            ),
            MetaDescriptionDraft(
                text=(
                    "Use BCBA mock exams to check readiness, find weak areas, "
                    "and plan your next study steps before test day."
                ),
                rationale="Frames the page around user outcomes instead of only the product.",
            ),
        ]

    def _direct_answer_block(self, topic: str) -> str:
        display_topic = self._display_topic(topic)
        return (
            f"A {display_topic} helps BCBA candidates practice exam-style questions, "
            "check readiness, and identify study gaps before the real exam. "
            "A strong mock exam page should clearly explain what is included, "
            "how scoring works, whether answer explanations are provided, and "
            "how candidates should use the results in their study plan."
        )

    def _faq_drafts(self, weak_items: list[GapCoverageItem]) -> list[FaqDraft]:
        drafts = []
        for item in weak_items[:8]:
            drafts.append(
                FaqDraft(
                    question=item.question.question,
                    answer_angle=self._answer_angle(item.question.intent),
                    source_gap_status=item.status,
                )
            )
        return drafts

    def _section_drafts(self, weak_items: list[GapCoverageItem]) -> list[SectionDraft]:
        sections = []
        for item in weak_items[:6]:
            heading = self._heading_for_intent(item.question.intent)
            sections.append(
                SectionDraft(
                    heading=heading,
                    purpose=f"Answer the user question: {item.question.question}",
                    talking_points=self._talking_points(item.question.intent),
                )
            )
        return self._dedupe_sections(sections)

    def _schema_drafts(
        self,
        readiness: GeoReadinessResult,
        gap: GeoGapAnalysisResult,
    ) -> list[SchemaDraft]:
        drafts = [
            SchemaDraft(
                schema_type="Organization",
                purpose="Clarify the brand entity behind the website.",
                required_fields=["name", "url", "logo", "sameAs"],
            ),
            SchemaDraft(
                schema_type="WebSite",
                purpose="Help search systems understand the website entity.",
                required_fields=["name", "url"],
            ),
        ]
        if gap.missing_questions:
            drafts.append(
                SchemaDraft(
                    schema_type="FAQPage",
                    purpose="Represent visible FAQ content after it is added to the page.",
                    required_fields=["mainEntity", "Question", "acceptedAnswer"],
                )
            )
        if readiness.dimension_scores.get("schema", 0) < 100:
            drafts.append(
                SchemaDraft(
                    schema_type="Product",
                    purpose="Describe the mock exam product if pricing/offers are visible on the page.",
                    required_fields=["name", "description", "offers"],
                )
            )
        return drafts

    def _editorial_notes(self, word_count: int) -> list[str]:
        notes = [
            "Treat these drafts as a content brief. Confirm product facts before publishing.",
            "Do not claim pass-rate, BACB affiliation, or guarantee language unless verified.",
            "When adding FAQPage schema, make sure each Q&A is visible on the page.",
        ]
        if word_count < 1200:
            notes.append(
                "Consider expanding the page with deeper detail on format, scoring, review flow, and study use cases."
            )
        return notes

    def _answer_angle(self, intent: str) -> str:
        angles = {
            "pricing": "State the current price or explain where pricing is shown. Avoid vague discount claims.",
            "scoring": "Explain how users receive scores and what the score helps them decide next.",
            "coverage": "List the exam domains or content areas covered by the mock exam.",
            "updates": "Clarify whether the content follows the current BACB test content outline.",
            "review": "Explain whether candidates can review missed questions and answer explanations.",
            "access": "Explain device access, online availability, and whether progress is saved.",
            "trust": "Identify who wrote or reviewed the questions and what credentials they have.",
        }
        return angles.get(intent, "Answer directly in 2-4 sentences with specific, verifiable details.")

    def _heading_for_intent(self, intent: str) -> str:
        headings = {
            "pricing": "BCBA Mock Exam Pricing",
            "scoring": "How Scoring and Review Work",
            "coverage": "Exam Domains and Content Areas Covered",
            "updates": "Alignment With the Current BACB Outline",
            "review": "Reviewing Missed Questions and Explanations",
            "access": "Online Access and Study Workflow",
            "trust": "Question Review and Author Credentials",
        }
        return headings.get(intent, f"Improve {intent.replace('_', ' ').title()} Coverage")

    def _talking_points(self, intent: str) -> list[str]:
        points = {
            "pricing": ["Current offer", "What is included", "Refund or access terms if applicable"],
            "scoring": ["Score shown after completion", "How to interpret weak areas", "Next study steps"],
            "coverage": ["Measurement", "Assessment", "Ethics", "Intervention", "Supervision if applicable"],
            "updates": ["Relevant BACB outline version", "Last review/update date", "How updates are handled"],
            "review": ["Missed question review", "Answer explanations", "Retake or progress behavior"],
            "access": ["Online access", "Mobile/browser compatibility", "Login or account requirements"],
            "trust": ["Reviewer credentials", "ABA/BCBA experience", "Editorial review process"],
        }
        return points.get(intent, ["Direct answer", "Specific details", "Evidence or example"])

    def _dedupe_sections(self, sections: list[SectionDraft]) -> list[SectionDraft]:
        seen = set()
        deduped = []
        for section in sections:
            if section.heading in seen:
                continue
            seen.add(section.heading)
            deduped.append(section)
        return deduped

    def _display_topic(self, topic: str) -> str:
        replacements = {
            "bcba": "BCBA",
            "bacb": "BACB",
            "aba": "ABA",
        }
        words = []
        for word in topic.split():
            lower = word.lower()
            words.append(replacements.get(lower, lower.capitalize()))
        return " ".join(words)

from __future__ import annotations

import re
from collections import Counter
from typing import Optional

from app.schemas.geo_gap import GapCoverageItem, GapQuestion, GeoGapAnalysisResult
from app.schemas.page import AnalyzePageResponse
from app.services.geo_gap.question_bank import QuestionBank


ANALYZER_VERSION = "geo-gap-rules-v0.1"

STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "are",
    "can",
    "does",
    "each",
    "exam",
    "for",
    "from",
    "have",
    "help",
    "how",
    "included",
    "into",
    "the",
    "this",
    "use",
    "what",
    "when",
    "which",
    "with",
}


class GeoGapAnalyzer:
    """Rule-based question coverage analyzer."""

    def __init__(self, question_bank: Optional[QuestionBank] = None) -> None:
        self.question_bank = question_bank or QuestionBank()

    def analyze(
        self,
        analysis_run_id: int,
        analysis: AnalyzePageResponse,
        target_keyword: Optional[str],
    ) -> GeoGapAnalysisResult:
        questions = self.question_bank.generate(target_keyword)
        text = analysis.page.main_text
        items = [self._score_question(question, text) for question in questions]

        covered_count = sum(1 for item in items if item.status == "covered")
        partial_count = sum(1 for item in items if item.status == "partial")
        missing_count = sum(1 for item in items if item.status == "missing")
        weighted_score = (
            sum(self._status_points(item.status) * item.question.priority for item in items)
            / sum(item.question.priority for item in items)
        )

        missing_questions = [
            item.question for item in items if item.status in {"partial", "missing"}
        ]

        return GeoGapAnalysisResult(
            analysis_run_id=analysis_run_id,
            analyzer_version=ANALYZER_VERSION,
            overall_coverage_score=round(weighted_score * 100, 2),
            covered_count=covered_count,
            partial_count=partial_count,
            missing_count=missing_count,
            items=items,
            missing_questions=missing_questions,
            recommendations=self._recommendations(items),
        )

    def _score_question(self, question: GapQuestion, text: str) -> GapCoverageItem:
        keywords = self._keywords(question.question)
        lower_text = text.lower()

        if question.question.rstrip("?").lower() in lower_text:
            coverage_score = 1.0
        else:
            matched = sum(1 for keyword in keywords if keyword in lower_text)
            coverage_score = matched / max(len(keywords), 1)

        if coverage_score >= 0.65:
            status = "covered"
        elif coverage_score >= 0.35:
            status = "partial"
        else:
            status = "missing"

        evidence = self._best_evidence(text, keywords) if status != "missing" else None
        return GapCoverageItem(
            question=question,
            status=status,
            coverage_score=round(coverage_score, 2),
            evidence=evidence,
            recommendation=self._recommendation(question, status),
        )

    def _keywords(self, question: str) -> list[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9-]+", question.lower())
        return [
            word
            for word in words
            if len(word) >= 4 and word not in STOPWORDS
        ]

    def _best_evidence(self, text: str, keywords: list[str]) -> Optional[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        if not sentences:
            return None

        keyword_set = set(keywords)
        scored = []
        for sentence in sentences:
            sentence_words = set(self._keywords(sentence))
            scored.append((len(keyword_set & sentence_words), sentence.strip()))

        best_score, best_sentence = max(scored, key=lambda item: item[0])
        if best_score <= 0:
            return None
        return best_sentence[:300]

    def _recommendation(self, question: GapQuestion, status: str) -> str:
        if status == "covered":
            return "Keep this topic visible and easy to scan."
        if status == "partial":
            return f"Expand the page section that answers: {question.question}"
        return f"Add a clear answer for: {question.question}"

    def _recommendations(self, items: list[GapCoverageItem]) -> list[str]:
        grouped = Counter(item.question.intent for item in items if item.status != "covered")
        recommendations = []
        for intent, _count in grouped.most_common():
            recommendations.append(f"Strengthen {intent.replace('_', ' ')} coverage.")
        return recommendations

    def _status_points(self, status: str) -> float:
        if status == "covered":
            return 1.0
        if status == "partial":
            return 0.5
        return 0.0

from __future__ import annotations

from typing import Optional

from app.schemas.geo_gap import GapQuestion


class QuestionBank:
    """Generates a deterministic first-pass question set.

    Later we can replace or extend this with an LLM Intent Agent. Keeping it as
    a separate class makes that future swap small.
    """

    def generate(self, target_keyword: Optional[str]) -> list[GapQuestion]:
        topic = target_keyword or "BCBA mock exam"
        questions = [
            ("definition", f"What is a {topic}?"),
            ("benefit", f"How does a {topic} help with BCBA exam prep?"),
            ("format", "How similar is the mock exam to the real BCBA exam format?"),
            ("coverage", "Which BCBA exam content areas or domains are covered?"),
            ("explanations", "Are answer explanations included for each question?"),
            ("scoring", "How is the mock exam scored?"),
            ("pricing", "How much does the BCBA mock exam cost?"),
            ("sample", "Is there a free sample or free BCBA practice test?"),
            ("difficulty", "How difficult are the practice questions compared with the real exam?"),
            ("study_plan", "How should a candidate use mock exams in a study plan?"),
            ("updates", "Is the mock exam updated for the current BACB test content outline?"),
            ("access", "Can candidates take the mock exam online or on mobile?"),
            ("review", "Can candidates review missed questions after finishing?"),
            ("audience", "Who is this BCBA mock exam best for?"),
            ("trust", "Who created or reviewed the BCBA mock exam questions?"),
        ]
        return [
            GapQuestion(
                id=f"q{index:02d}",
                question=question,
                intent=intent,
                priority=1 if index <= 8 else 2,
            )
            for index, (intent, question) in enumerate(questions, start=1)
        ]

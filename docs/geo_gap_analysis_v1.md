# GEO Gap Analysis v1

`GEO Gap Analysis v1` checks whether a page appears to cover the user questions
that matter for a target topic.

This first version is deterministic. It uses a built-in question bank and simple
keyword overlap to create a stable baseline before adding LLM judgment.

## Flow

```text
POST /api/v1/analyze/page
  -> save analysis_run

POST /api/v1/geo/gap-analysis/{analysis_run_id}
  -> generate question set
  -> compare questions with extracted page text
  -> classify each question as covered / partial / missing
  -> save geo_gap_analyses
```

## Why This Exists

GEO is not only about whether a page has title tags, schema, and headings.
Generative engines answer user questions. The page needs to cover the questions
people actually ask.

For BCBA Mock Exam, the first question bank includes topics such as:

- what a BCBA mock exam is
- how it helps exam prep
- whether answer explanations are included
- pricing
- scoring
- content areas covered
- free samples
- current BACB outline alignment
- review of missed questions
- who created or reviewed the questions

## Limitations

This version is intentionally simple:

- It does not understand meaning deeply.
- It may mark a question as partial if the right keywords appear but the answer
  is weak.
- It does not compare against competitors yet.

Future versions should add an LLM evaluator that reads the page text and judges
whether each question is truly answered with evidence.


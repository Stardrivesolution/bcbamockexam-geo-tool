# GEO Readiness v1

`GEO Readiness v1` is the first rule-based scoring layer.

It does not use an LLM yet. The goal is to create a stable baseline that checks
whether a page has the basic technical and structural signals needed before
semantic scoring begins.

## Flow

```text
POST /api/v1/analyze/page
  -> fetch and extract page data
  -> save analysis_runs.raw_result

POST /api/v1/geo/readiness/{analysis_run_id}
  -> load saved page data
  -> run deterministic rules
  -> save geo_readiness_assessments
```

## Current Dimensions

| Dimension | Checks |
|---|---|
| metadata | title, title length, meta description, meta length |
| crawlability | noindex, canonical, robots.txt check |
| structure | single H1, supporting headings, lists/tables, FAQ/question structure |
| content | enough text, substantial depth, direct-answer candidate, question signals |
| schema | JSON-LD presence, useful schema type |
| links | internal links, external/reference links |
| media | image presence, image alt coverage |

## Why The First Score Can Be High

This version only measures deterministic readiness. A page can score well here
because it has good technical and structural signals, while still needing better
semantic coverage.

Future versions should add:

- LLM answerability scoring
- user question coverage
- entity clarity scoring
- trust and evidence quality
- competitor comparison


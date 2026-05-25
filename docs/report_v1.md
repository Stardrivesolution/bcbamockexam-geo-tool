# Report v1

`Report v1` creates a Markdown report from the saved page analysis, GEO
Readiness score, and Gap Analysis.

## Flow

```text
POST /api/v1/analyze/page
  -> analysis_run_id

POST /api/v1/reports/geo/{analysis_run_id}
  -> auto-create missing readiness/gap results if needed
  -> save a Markdown report
  -> return report content
```

## Why This Matters

Earlier endpoints answer separate questions:

- What did the crawler extract?
- What is the readiness score?
- Which user questions are missing?

The report combines those answers into one artifact that a teammate can read
and use to update the website.

## Current Sections

- Page summary
- GEO Readiness Score
- Gap Coverage Score
- Readiness dimensions
- Top readiness issues
- Content gaps
- Recommended next actions

## Limitations

This version is Markdown only. HTML/PDF/DOCX export can be added later without
changing the scoring services.


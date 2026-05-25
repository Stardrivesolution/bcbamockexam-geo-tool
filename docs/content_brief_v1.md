# Content Brief v1

`Content Brief v1` turns GEO findings into a human-reviewable writing brief.

It is intentionally not a full autopilot writer yet. The goal is to help the
team decide what to add or rewrite on the page without inventing product facts.

## Flow

```text
POST /api/v1/analyze/page
  -> analysis_run_id

POST /api/v1/content/brief/{analysis_run_id}
  -> auto-create missing readiness/gap artifacts
  -> generate title options, meta options, FAQ drafts, sections, and schema suggestions
  -> save content_briefs
```

## Current Output

- title options
- meta description options
- direct answer block
- FAQ draft list
- section draft list
- schema suggestions
- editorial notes

## Editorial Safety

The system should not invent:

- pass-rate claims
- BACB affiliation
- guarantees
- reviewer credentials
- pricing
- feature availability

Any feature-specific draft should be checked against the actual product before
publishing.


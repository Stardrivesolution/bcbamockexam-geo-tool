# BCBA Mock Exam GEO Tool

Company-internal GEO analysis, content optimization, and AI visibility tooling
for [bcbamockexam.com](https://bcbamockexam.com/).

The current product goal is to help us answer:

```text
1. Is a page technically and structurally ready for AI/search citation?
2. Which user questions are not covered well enough?
3. What content should we add or rewrite next?
4. Later: Are AI answer engines mentioning or citing us more often?
```

## Current Status

Last updated: 2026-05-25

| Area | Status | Notes |
|---|---|---|
| FastAPI backend | Done | API-first internal tool. |
| Project configuration | Done | BCBA Mock Exam project, target language, region, and competitors. |
| Page crawler/extractor | Done | Extracts title, meta, headings, text, links, images, JSON-LD, canonical, noindex, and structure signals. |
| GEO Readiness scoring | Done v1 | Rule-based baseline scoring. |
| Gap Analysis | Done v1 | Static and intent-question based coverage analysis. |
| Markdown report | Done v1 | Combines page analysis, readiness, and gaps. |
| Content Brief | Done v1 | Generates title/meta/FAQ/section/schema suggestions for human review. |
| LLM provider | Done v1 | OpenAI-compatible client; DeepSeek configured through `.env`. |
| Intent Agent | Done v1 | LLM or static question generation. |
| LLM Gap Evaluator | Not started | Next recommended step. |
| Competitor analysis | Not started | Planned after LLM evaluator. |
| AI Visibility Monitor | Not started | Planned later. |
| Frontend UI | Not started | FastAPI docs are enough for now. |

## Quick Start

```bash
git clone https://github.com/Stardrivesolution/bcbamockexam-geo-tool.git
cd bcbamockexam-geo-tool
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. python scripts/init_db.py
PYTHONPATH=. python scripts/seed_bcbamockexam_project.py
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

Do not commit `.env`.

Use `.env.example` as the template:

```env
APP_NAME="GEO Internal Tool"
APP_ENV="local"
APP_DEBUG=true
HTTP_TIMEOUT_SECONDS=20
MAX_HTML_BYTES=3000000
DATABASE_URL="sqlite:///./geo_internal_tool.db"
LLM_PROVIDER="deepseek"
LLM_API_KEY=""
LLM_BASE_URL="https://api.deepseek.com"
LLM_MODEL="deepseek-chat"
LLM_TIMEOUT_SECONDS=60
```

DeepSeek works through the OpenAI-compatible LLM client. Put the real key only
in local `.env`.

## Main Workflow

### 1. Analyze A Page

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze/page \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "url": "https://bcbamockexam.com/",
    "target_keyword": "BCBA mock exam",
    "language": "en"
  }'
```

Save the returned `analysis_run_id`.

### 2. Score GEO Readiness

```bash
curl -X POST http://127.0.0.1:8000/api/v1/geo/readiness/{analysis_run_id}
```

### 3. Generate Intent Questions

Static mode:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/intent/questions/{analysis_run_id}?use_llm=false"
```

LLM mode:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/intent/questions/{analysis_run_id}?use_llm=true"
```

### 4. Run Gap Analysis

Default static questions:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/geo/gap-analysis/{analysis_run_id}
```

Use latest generated intent question set:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/geo/gap-analysis/{analysis_run_id}?use_latest_intent=true"
```

### 5. Generate Report

```bash
curl -X POST http://127.0.0.1:8000/api/v1/reports/geo/{analysis_run_id}
```

### 6. Generate Content Brief

```bash
curl -X POST http://127.0.0.1:8000/api/v1/content/brief/{analysis_run_id}
```

## What The Tool Currently Produces

For the BCBA Mock Exam homepage, current rule-based outputs have shown:

```text
GEO Readiness Score: 96.36
Gap Coverage Score: 72.73
```

Detected improvement themes include:

```text
- covered BCBA content areas / domains
- mock exam scoring explanation
- current BACB outline alignment
- online/mobile access
- missed question review
- author/reviewer trust signals
```

## API Overview

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/projects` | List projects |
| `POST /api/v1/projects` | Create project |
| `POST /api/v1/analyze/page` | Crawl and extract page data |
| `GET /api/v1/analyze/runs` | List analysis runs |
| `POST /api/v1/geo/readiness/{analysis_run_id}` | Rule-based GEO readiness score |
| `POST /api/v1/geo/gap-analysis/{analysis_run_id}` | Question coverage analysis |
| `POST /api/v1/reports/geo/{analysis_run_id}` | Markdown GEO report |
| `POST /api/v1/content/brief/{analysis_run_id}` | Content optimization brief |
| `POST /api/v1/llm/smoke-test` | Test LLM provider |
| `POST /api/v1/intent/questions/{analysis_run_id}` | Static/LLM intent questions |

## Data Tables

```text
projects
pages
analysis_runs
geo_readiness_assessments
geo_gap_analyses
geo_reports
content_briefs
intent_question_sets
```

Everything important is linked to `analysis_run_id` so we can compare before
and after optimization.

## Architecture

```text
app/
  api/routes/       FastAPI route handlers
  core/             runtime config
  db/               SQLAlchemy models and session
  repositories/     database read/write layer
  schemas/          Pydantic request/response models
  services/         crawler, extractor, scoring, gap, reports, content, LLM
  utils/            shared helpers
```

Design principle:

```text
Routes should orchestrate.
Services should contain business logic.
Repositories should own database access.
Schemas should define stable data contracts.
```

## Useful Docs

- [Competitor selection](docs/competitor_selection.md)
- [Team environment and secrets](docs/team_environment.md)
- [LLM provider](docs/llm_provider.md)
- [GEO Readiness v1](docs/geo_readiness_v1.md)
- [GEO Gap Analysis v1](docs/geo_gap_analysis_v1.md)
- [Intent Agent v1](docs/intent_agent_v1.md)
- [Report v1](docs/report_v1.md)
- [Content Brief v1](docs/content_brief_v1.md)

## Development Workflow

Before starting:

```bash
git pull
```

After making changes:

```bash
PYTHONPATH=. pytest -q
git status
git add .
git commit -m "short clear message"
git push
```

## Next Recommended Step

Build `LLM Gap Evaluator v2`.

Goal:

```text
Instead of keyword overlap, use DeepSeek to judge whether the page truly
answers each generated user question, with evidence and covered/partial/missing
classification.
```

Suggested new modules:

```text
app/services/geo_gap/llm_evaluator.py
app/services/geo_gap/prompts.py
docs/llm_gap_evaluator_v2.md
```


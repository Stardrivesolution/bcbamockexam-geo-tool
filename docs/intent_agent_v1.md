# Intent Agent v1

`Intent Agent v1` generates the user questions used for GEO gap analysis.

The first implementation supports two modes:

- static fallback question bank
- LLM-generated question set through the OpenAI-compatible LLM client

DeepSeek is the default provider in `.env.example`, but the implementation is
provider-neutral.

## Static Mode

Static mode does not require an API key:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/intent/questions/1?use_llm=false"
```

## LLM Mode

LLM mode requires `LLM_API_KEY`:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/intent/questions/1?use_llm=true"
```

The generated question set is saved in:

```text
intent_question_sets
```

## Using The Latest Intent Set In Gap Analysis

After generating an intent question set, run:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/geo/gap-analysis/1?use_latest_intent=true"
```

This tells Gap Analysis to use the latest saved intent question set for that
analysis run instead of the static default question bank.

## Why This Matters

Static questions are stable, but generic. LLM-generated questions should be
closer to real user behavior, especially for buyer-intent and trust questions.


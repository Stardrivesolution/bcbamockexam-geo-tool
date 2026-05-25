# LLM Provider

The project uses an OpenAI-compatible LLM adapter.

DeepSeek is the default provider for the first version, but the code should not
be written as DeepSeek-only. Qwen, OpenAI, or other OpenAI-compatible providers
can be used by changing environment variables.

## Environment

```env
LLM_PROVIDER="deepseek"
LLM_API_KEY=""
LLM_BASE_URL="https://api.deepseek.com"
LLM_MODEL="deepseek-chat"
LLM_TIMEOUT_SECONDS=60
```

## Why OpenAI-Compatible

Many model providers expose the same chat completions interface. Keeping one
adapter gives us:

- provider switching through `.env`
- less duplicated code
- consistent request/response logging
- easier prompt versioning

## Smoke Test

After setting `LLM_API_KEY` in local `.env`, run:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/llm/smoke-test
```

Expected response contains:

```json
{
  "parsed_json": {
    "status": "ok"
  }
}
```

## Safety Rules

- Never commit `.env`.
- Never log API keys.
- Use JSON mode for structured evaluator outputs.
- Validate model output with Pydantic before saving business-critical results.
- Store prompt versions when model outputs are used for scoring.


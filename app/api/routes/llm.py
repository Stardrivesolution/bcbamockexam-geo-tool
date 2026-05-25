from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.services.llm.client import LlmNotConfiguredError, OpenAICompatibleLlmClient
from app.services.llm.schemas import LlmRequest, LlmResponse

router = APIRouter(prefix="/llm", tags=["llm"])


@router.post("/smoke-test", response_model=LlmResponse)
async def llm_smoke_test(
    settings: Settings = Depends(get_settings),
) -> LlmResponse:
    try:
        client = OpenAICompatibleLlmClient(settings)
        return client.generate_json(
            LlmRequest(
                system_prompt="You are a test assistant. Return only valid JSON.",
                user_prompt='Return {"status":"ok","purpose":"llm smoke test"}.',
                temperature=0,
                max_tokens=80,
                response_format="json",
            ),
            prompt_version="llm-smoke-test-v0.1",
        )
    except LlmNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

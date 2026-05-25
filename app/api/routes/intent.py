from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.intent import IntentQuestionSetRepository
from app.repositories.projects import ProjectRepository
from app.schemas.intent import IntentQuestionSet
from app.schemas.project import ProjectRead
from app.services.intent.llm_intent_generator import LlmIntentGenerator
from app.services.intent.static_intent_generator import StaticIntentGenerator
from app.services.llm.client import LlmNotConfiguredError, OpenAICompatibleLlmClient

router = APIRouter(prefix="/intent", tags=["intent"])


@router.post("/questions/{analysis_run_id}", response_model=IntentQuestionSet)
async def generate_intent_questions(
    analysis_run_id: int,
    use_llm: bool = True,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> IntentQuestionSet:
    run = AnalysisRunRepository(db).get(analysis_run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")
    if not run.target_keyword:
        raise HTTPException(status_code=400, detail="Analysis run has no target keyword")

    project = None
    if run.project_id:
        project_model = ProjectRepository(db).get(run.project_id)
        if project_model:
            project = ProjectRead.model_validate(project_model)

    try:
        if use_llm:
            generator = LlmIntentGenerator(OpenAICompatibleLlmClient(settings))
        else:
            generator = StaticIntentGenerator()
        result = generator.generate(
            target_keyword=run.target_keyword,
            project=project,
            analysis_run_id=analysis_run_id,
        )
    except LlmNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Intent generation failed: {exc}") from exc

    saved = IntentQuestionSetRepository(db).save(result)
    result.id = saved.id
    result.created_at = saved.created_at
    return result


@router.get("/{question_set_id}", response_model=IntentQuestionSet)
async def get_intent_question_set(
    question_set_id: int,
    db: Session = Depends(get_db),
) -> IntentQuestionSet:
    model = IntentQuestionSetRepository(db).get(question_set_id)
    if not model:
        raise HTTPException(status_code=404, detail="Intent question set not found")
    result = IntentQuestionSet.model_validate(model.raw_result)
    result.id = model.id
    result.created_at = model.created_at
    return result

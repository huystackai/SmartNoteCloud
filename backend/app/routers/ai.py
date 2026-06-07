from fastapi import APIRouter, Depends

from app.ai.ai_service import ai_service
from app.auth.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AiSuggestRequest, AiSuggestResponse, AiSummaryResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/suggest", response_model=AiSuggestResponse)
async def suggest(
    payload: AiSuggestRequest,
    _: User = Depends(get_current_user),
) -> AiSuggestResponse:
    suggestions = await ai_service.suggest(payload.task, payload.mode)
    return AiSuggestResponse(suggestions=suggestions)


@router.post("/breakdown", response_model=AiSuggestResponse)
async def breakdown(payload: AiSuggestRequest, _: User = Depends(get_current_user)) -> AiSuggestResponse:
    suggestions = await ai_service.suggest(payload.task, "breakdown")
    return AiSuggestResponse(suggestions=suggestions)


@router.post("/summarize", response_model=AiSummaryResponse)
async def summarize(payload: AiSuggestRequest, _: User = Depends(get_current_user)) -> AiSummaryResponse:
    suggestions = await ai_service.suggest(payload.task, "summarize")
    return AiSummaryResponse(summary=suggestions[0])


@router.post("/productivity", response_model=AiSuggestResponse)
async def productivity(payload: AiSuggestRequest, _: User = Depends(get_current_user)) -> AiSuggestResponse:
    suggestions = await ai_service.suggest(payload.task, "productivity")
    return AiSuggestResponse(suggestions=suggestions)

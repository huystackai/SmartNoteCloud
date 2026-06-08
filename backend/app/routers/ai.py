from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.ai_service import ai_service
from app.auth.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.ai import AIChatMessage
from app.models.user import User
from app.schemas.ai import (
    AiChatHistoryResponse,
    AiChatRequest,
    AiChatResponse,
    AiSuggestRequest,
    AiSuggestResponse,
    AiSummaryResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


def _chat_usage(db: Session, user_id: int) -> int:
    return int(db.scalar(select(func.count(AIChatMessage.id)).where(AIChatMessage.user_id == user_id)) or 0)


def _remaining(used: int) -> int:
    return max(settings.ai_chat_limit - used, 0)


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


@router.get("/chat/history", response_model=AiChatHistoryResponse)
def chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AiChatHistoryResponse:
    used = _chat_usage(db, current_user.id)
    messages = (
        db.scalars(
            select(AIChatMessage)
            .where(AIChatMessage.user_id == current_user.id)
            .order_by(AIChatMessage.created_at.desc(), AIChatMessage.id.desc())
            .limit(20)
        )
        .all()
    )
    messages.reverse()
    return AiChatHistoryResponse(
        messages=messages,
        used=used,
        remaining=_remaining(used),
        limit=settings.ai_chat_limit,
    )


@router.post("/chat", response_model=AiChatResponse, status_code=status.HTTP_201_CREATED)
async def chat(
    payload: AiChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AiChatResponse:
    db.execute(select(User.id).where(User.id == current_user.id).with_for_update()).scalar_one()
    used = _chat_usage(db, current_user.id)
    if used >= settings.ai_chat_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn đã dùng hết {settings.ai_chat_limit} lượt hỏi AI.",
        )

    rule_answer = ai_service.rule_based_chat(payload.question)
    source = "rule" if rule_answer else "ai"
    answer = rule_answer or await ai_service.chat_answer(payload.question)

    message = AIChatMessage(
        user_id=current_user.id,
        question=payload.question.strip(),
        answer=answer.strip(),
        source=source,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    new_used = used + 1
    return AiChatResponse(
        message=message,
        used=new_used,
        remaining=_remaining(new_used),
        limit=settings.ai_chat_limit,
    )

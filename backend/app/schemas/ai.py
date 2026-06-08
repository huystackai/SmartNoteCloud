from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AiMode = Literal["breakdown", "summarize", "subtasks", "productivity"]
AiChatSource = Literal["rule", "ai"]


class AiSuggestRequest(BaseModel):
    task: str = Field(min_length=2, max_length=2000)
    mode: AiMode = "breakdown"


class AiSuggestResponse(BaseModel):
    suggestions: list[str]


class AiSummaryResponse(BaseModel):
    summary: str


class AiChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class AiChatMessageRead(BaseModel):
    id: int
    question: str
    answer: str
    source: AiChatSource
    created_at: datetime

    model_config = {"from_attributes": True}


class AiChatResponse(BaseModel):
    message: AiChatMessageRead
    used: int
    remaining: int
    limit: int


class AiChatHistoryResponse(BaseModel):
    messages: list[AiChatMessageRead]
    used: int
    remaining: int
    limit: int

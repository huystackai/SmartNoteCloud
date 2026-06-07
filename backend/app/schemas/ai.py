from typing import Literal

from pydantic import BaseModel, Field

AiMode = Literal["breakdown", "summarize", "subtasks", "productivity"]


class AiSuggestRequest(BaseModel):
    task: str = Field(min_length=2, max_length=2000)
    mode: AiMode = "breakdown"


class AiSuggestResponse(BaseModel):
    suggestions: list[str]


class AiSummaryResponse(BaseModel):
    summary: str

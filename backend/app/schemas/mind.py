from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

BlockType = Literal["paragraph", "heading", "list", "quote", "code"]


class WorkspaceRead(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class BlockRead(BaseModel):
    id: int
    page_id: int
    type: str
    content: str
    order_index: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlockWrite(BaseModel):
    id: int | None = None
    type: BlockType = "paragraph"
    content: str = Field(default="", max_length=8000)


class BlockBatchUpdate(BaseModel):
    blocks: list[BlockWrite] = Field(default_factory=list, max_length=80)


class PageRead(BaseModel):
    id: int
    workspace_id: int
    title: str
    icon: str | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PageDetail(PageRead):
    blocks: list[BlockRead] = Field(default_factory=list)


class PageCreate(BaseModel):
    workspace_id: int | None = None
    title: str = Field(min_length=1, max_length=180)
    icon: str | None = Field(default=None, max_length=20)


class PageUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    icon: str | None = Field(default=None, max_length=20)
    summary: str | None = Field(default=None, max_length=12000)


class DeckRead(BaseModel):
    id: int
    workspace_id: int
    name: str
    description: str | None = None
    new_per_day: int
    review_per_day: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DeckCreate(BaseModel):
    workspace_id: int | None = None
    name: str = Field(min_length=2, max_length=140)
    description: str | None = Field(default=None, max_length=2000)
    new_per_day: int = Field(default=12, ge=1, le=100)
    review_per_day: int = Field(default=60, ge=1, le=300)


class CardRead(BaseModel):
    id: int
    deck_id: int
    page_id: int | None = None
    block_id: int | None = None
    type: str
    front: str
    back: str
    source_text: str | None = None
    ease: float
    interval: int
    repetition: int
    due_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class CardCreate(BaseModel):
    deck_id: int
    page_id: int | None = None
    block_id: int | None = None
    front: str = Field(min_length=1, max_length=4000)
    back: str = Field(min_length=1, max_length=8000)
    source_text: str | None = Field(default=None, max_length=12000)
    type: str = Field(default="basic", max_length=30)


class ReviewCreate(BaseModel):
    card_id: int
    grade: int = Field(ge=0, le=3)


class ReviewResult(BaseModel):
    card: CardRead
    label: str


class SearchResult(BaseModel):
    page: PageRead
    snippet: str


class ReviewStats(BaseModel):
    pages: int
    blocks: int
    decks: int
    cards: int
    due_cards: int
    studied_today: int


class BootstrapRead(BaseModel):
    workspace: WorkspaceRead
    pages: list[PageRead]
    decks: list[DeckRead]
    stats: ReviewStats


class AiSummaryRead(BaseModel):
    summary: str


class GeneratedCard(BaseModel):
    front: str
    back: str
    source_text: str | None = None


class GeneratedCardsRead(BaseModel):
    cards: list[GeneratedCard]

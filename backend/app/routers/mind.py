from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.ai.ai_service import ai_service
from app.auth.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.mind import (
    AiSummaryRead,
    BlockBatchUpdate,
    BootstrapRead,
    CardCreate,
    CardRead,
    DeckCreate,
    DeckRead,
    GeneratedCardsRead,
    PageCreate,
    PageDetail,
    PageRead,
    PageUpdate,
    ReviewCreate,
    ReviewResult,
    ReviewStats,
    SearchResult,
    WorkspaceCreate,
    WorkspaceRead,
)
from app.services import mind_service

router = APIRouter(prefix="/mind", tags=["minddeck"])


@router.get("/bootstrap", response_model=BootstrapRead)
def bootstrap(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> BootstrapRead:
    workspace = mind_service.ensure_default_workspace(db, current_user)
    return BootstrapRead(
        workspace=workspace,
        pages=mind_service.list_pages(db, current_user, workspace.id),
        decks=mind_service.list_decks(db, current_user, workspace.id),
        stats=mind_service.stats(db, current_user),
    )


@router.post("/workspaces", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.create_workspace(db, current_user, payload.name)


@router.get("/pages", response_model=list[PageRead])
def pages(
    workspace_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.list_pages(db, current_user, workspace_id)


@router.post("/pages", response_model=PageDetail, status_code=status.HTTP_201_CREATED)
def create_page(
    payload: PageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.create_page(db, current_user, payload)


@router.get("/pages/{page_id}", response_model=PageDetail)
def page_detail(page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return mind_service.get_owned_page(db, current_user, page_id)


@router.patch("/pages/{page_id}", response_model=PageDetail)
def update_page(
    page_id: int,
    payload: PageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.update_page(db, current_user, page_id, payload)


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_page(page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    mind_service.delete_page(db, current_user, page_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/pages/{page_id}/blocks", response_model=PageDetail)
def save_blocks(
    page_id: int,
    payload: BlockBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.replace_blocks(db, current_user, page_id, payload.blocks)


@router.post("/pages/{page_id}/summarize", response_model=AiSummaryRead)
async def summarize_page(page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = mind_service.get_owned_page(db, current_user, page_id)
    summary = await ai_service.summarize_note(page.title, mind_service.page_text(page))
    page.summary = summary
    db.commit()
    return AiSummaryRead(summary=summary)


@router.post("/pages/{page_id}/generate-cards", response_model=GeneratedCardsRead)
async def generate_cards(page_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    page = mind_service.get_owned_page(db, current_user, page_id)
    cards = await ai_service.generate_flashcards(page.title, mind_service.page_text(page))
    return GeneratedCardsRead(cards=cards)


@router.get("/decks", response_model=list[DeckRead])
def decks(
    workspace_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.list_decks(db, current_user, workspace_id)


@router.post("/decks", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(
    payload: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.create_deck(db, current_user, payload)


@router.get("/decks/{deck_id}/cards", response_model=list[CardRead])
def cards(
    deck_id: int,
    due: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.list_cards(db, current_user, deck_id, due_only=due)


@router.post("/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(
    payload: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.create_card(db, current_user, payload)


@router.post("/reviews", response_model=ReviewResult)
def review_card(
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    card, label = mind_service.apply_review(db, current_user, payload.card_id, payload.grade)
    return ReviewResult(card=card, label=label)


@router.get("/stats", response_model=ReviewStats)
def stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return mind_service.stats(db, current_user)


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(min_length=1, max_length=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mind_service.search_pages(db, current_user, q)

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.mind import Block, Card, CardReview, Deck, Page, Workspace
from app.models.user import User
from app.schemas.mind import BlockWrite, CardCreate, DeckCreate, PageCreate, PageUpdate, ReviewStats, SearchResult


STARTER_BLOCKS = [
    ("heading", "MindDeckNote Lite"),
    ("paragraph", "Ghi note theo block, tóm tắt bằng AI và biến ý chính thành flashcard để ôn tập."),
    ("list", "Demo Cloud Computing: React, FastAPI, PostgreSQL, Nginx, Docker Compose trên AWS EC2."),
    ("quote", "Một hệ thống nhỏ nhưng đủ lớp cloud: reverse proxy, container network, database volume và external AI API."),
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_default_workspace(db: Session, user: User) -> Workspace:
    workspace = db.scalar(select(Workspace).where(Workspace.owner_id == user.id).order_by(Workspace.id))
    if workspace:
        return workspace

    workspace = Workspace(owner_id=user.id, name="MindDeck Workspace")
    db.add(workspace)
    db.flush()

    page = Page(workspace_id=workspace.id, title="Cloud Computing Project", icon="note")
    db.add(page)
    db.flush()

    for index, (block_type, content) in enumerate(STARTER_BLOCKS):
        db.add(Block(page_id=page.id, type=block_type, content=content, order_index=index))

    db.add(Deck(workspace_id=workspace.id, name="Cloud Computing", description="Flashcards generated from project notes."))
    db.commit()
    db.refresh(workspace)
    return workspace


def create_workspace(db: Session, user: User, name: str) -> Workspace:
    workspace = Workspace(owner_id=user.id, name=name)
    db.add(workspace)
    db.flush()
    db.add(Deck(workspace_id=workspace.id, name="Default Deck", description="Cards created from notes in this workspace."))
    db.commit()
    db.refresh(workspace)
    return workspace


def get_owned_workspace(db: Session, user: User, workspace_id: int) -> Workspace:
    workspace = db.get(Workspace, workspace_id)
    if not workspace or workspace.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return workspace


def get_owned_page(db: Session, user: User, page_id: int) -> Page:
    page = db.scalar(
        select(Page)
        .join(Workspace)
        .options(selectinload(Page.blocks))
        .where(and_(Page.id == page_id, Workspace.owner_id == user.id))
    )
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return page


def get_owned_deck(db: Session, user: User, deck_id: int) -> Deck:
    deck = db.scalar(select(Deck).join(Workspace).where(and_(Deck.id == deck_id, Workspace.owner_id == user.id)))
    if not deck:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck


def get_owned_card(db: Session, user: User, card_id: int) -> Card:
    card = db.scalar(
        select(Card)
        .join(Deck)
        .join(Workspace)
        .where(and_(Card.id == card_id, Workspace.owner_id == user.id))
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    return card


def page_text(page: Page) -> str:
    blocks = sorted(page.blocks, key=lambda block: block.order_index)
    return "\n".join(block.content.strip() for block in blocks if block.content.strip())


def list_pages(db: Session, user: User, workspace_id: int | None = None) -> list[Page]:
    workspace = get_owned_workspace(db, user, workspace_id) if workspace_id else ensure_default_workspace(db, user)
    return list(
        db.scalars(
            select(Page)
            .where(Page.workspace_id == workspace.id)
            .order_by(Page.updated_at.desc(), Page.id.desc())
        )
    )


def create_page(db: Session, user: User, payload: PageCreate) -> Page:
    workspace = get_owned_workspace(db, user, payload.workspace_id) if payload.workspace_id else ensure_default_workspace(db, user)
    page = Page(workspace_id=workspace.id, title=payload.title, icon=payload.icon)
    db.add(page)
    db.flush()
    db.add(Block(page_id=page.id, type="paragraph", content="", order_index=0))
    db.commit()
    return get_owned_page(db, user, page.id)


def update_page(db: Session, user: User, page_id: int, payload: PageUpdate) -> Page:
    page = get_owned_page(db, user, page_id)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(page, key, value)
    db.commit()
    return get_owned_page(db, user, page_id)


def delete_page(db: Session, user: User, page_id: int) -> None:
    page = get_owned_page(db, user, page_id)
    db.delete(page)
    db.commit()


def replace_blocks(db: Session, user: User, page_id: int, blocks: list[BlockWrite]) -> Page:
    page = get_owned_page(db, user, page_id)
    db.query(Block).filter(Block.page_id == page.id).delete(synchronize_session=False)
    for index, block_data in enumerate(blocks):
        db.add(
            Block(
                page_id=page.id,
                type=block_data.type,
                content=block_data.content,
                order_index=index,
            )
        )
    page.updated_at = utc_now()
    db.commit()
    return get_owned_page(db, user, page_id)


def list_decks(db: Session, user: User, workspace_id: int | None = None) -> list[Deck]:
    workspace = get_owned_workspace(db, user, workspace_id) if workspace_id else ensure_default_workspace(db, user)
    return list(db.scalars(select(Deck).where(Deck.workspace_id == workspace.id).order_by(Deck.id)))


def create_deck(db: Session, user: User, payload: DeckCreate) -> Deck:
    workspace = get_owned_workspace(db, user, payload.workspace_id) if payload.workspace_id else ensure_default_workspace(db, user)
    deck = Deck(
        workspace_id=workspace.id,
        name=payload.name,
        description=payload.description,
        new_per_day=payload.new_per_day,
        review_per_day=payload.review_per_day,
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck


def create_card(db: Session, user: User, payload: CardCreate) -> Card:
    get_owned_deck(db, user, payload.deck_id)
    if payload.page_id:
        get_owned_page(db, user, payload.page_id)

    card = Card(**payload.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def list_cards(db: Session, user: User, deck_id: int, due_only: bool = False) -> list[Card]:
    get_owned_deck(db, user, deck_id)
    query = select(Card).where(Card.deck_id == deck_id)
    if due_only:
        query = query.where(Card.due_at <= utc_now())
    return list(db.scalars(query.order_by(Card.due_at.asc(), Card.id.asc())))


def apply_review(db: Session, user: User, card_id: int, grade: int) -> tuple[Card, str]:
    card = get_owned_card(db, user, card_id)
    labels = {0: "Again", 1: "Hard", 2: "Good", 3: "Easy"}

    ease = max(1.3, card.ease + {0: -0.25, 1: -0.1, 2: 0.0, 3: 0.15}[grade])
    if grade < 2:
        repetition = 0
        interval = 1
    else:
        repetition = card.repetition + 1
        if repetition == 1:
            interval = 1
        elif repetition == 2:
            interval = 6
        else:
            multiplier = ease + (0.35 if grade == 3 else 0)
            interval = max(1, round(card.interval * multiplier))

    due_at = utc_now() + timedelta(days=interval)
    card.ease = ease
    card.interval = interval
    card.repetition = repetition
    card.due_at = due_at

    db.add(
        CardReview(
            card_id=card.id,
            user_id=user.id,
            grade=grade,
            ease=ease,
            interval=interval,
            repetition=repetition,
            due_at=due_at,
        )
    )
    db.commit()
    db.refresh(card)
    return card, labels[grade]


def stats(db: Session, user: User) -> ReviewStats:
    workspace = ensure_default_workspace(db, user)
    today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
    page_count = db.scalar(select(func.count(Page.id)).where(Page.workspace_id == workspace.id)) or 0
    block_count = db.scalar(select(func.count(Block.id)).join(Page).where(Page.workspace_id == workspace.id)) or 0
    deck_count = db.scalar(select(func.count(Deck.id)).where(Deck.workspace_id == workspace.id)) or 0
    card_count = db.scalar(select(func.count(Card.id)).join(Deck).where(Deck.workspace_id == workspace.id)) or 0
    due_count = (
        db.scalar(select(func.count(Card.id)).join(Deck).where(and_(Deck.workspace_id == workspace.id, Card.due_at <= utc_now())))
        or 0
    )
    studied_today = (
        db.scalar(
            select(func.count(CardReview.id))
            .join(Card)
            .join(Deck)
            .where(and_(Deck.workspace_id == workspace.id, CardReview.user_id == user.id, CardReview.reviewed_at >= today_start))
        )
        or 0
    )
    return ReviewStats(
        pages=page_count,
        blocks=block_count,
        decks=deck_count,
        cards=card_count,
        due_cards=due_count,
        studied_today=studied_today,
    )


def search_pages(db: Session, user: User, query: str) -> list[SearchResult]:
    workspace = ensure_default_workspace(db, user)
    term = f"%{query.strip()}%"
    if not query.strip():
        return []

    pages = list(
        db.scalars(
            select(Page)
            .outerjoin(Block)
            .options(selectinload(Page.blocks))
            .where(and_(Page.workspace_id == workspace.id, or_(Page.title.ilike(term), Block.content.ilike(term))))
            .order_by(Page.updated_at.desc())
            .distinct()
            .limit(12)
        )
    )
    results = []
    for page in pages:
        text = page_text(page)
        snippet = text[:180] if text else page.summary or ""
        results.append(SearchResult(page=page, snippet=snippet))
    return results

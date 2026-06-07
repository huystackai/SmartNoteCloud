from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    owner = relationship("User", back_populates="workspaces")
    pages = relationship("Page", back_populates="workspace", cascade="all, delete-orphan")
    decks = relationship("Deck", back_populates="workspace", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    icon: Mapped[str | None] = mapped_column(String(20), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    workspace = relationship("Workspace", back_populates="pages")
    blocks = relationship("Block", back_populates="page", cascade="all, delete-orphan", order_by="Block.order_index")
    cards = relationship("Card", back_populates="page")


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    page_id: Mapped[int] = mapped_column(ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="paragraph")
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    page = relationship("Page", back_populates="blocks")
    cards = relationship("Card", back_populates="block")


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_per_day: Mapped[int] = mapped_column(Integer, nullable=False, server_default="12")
    review_per_day: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    workspace = relationship("Workspace", back_populates="decks")
    cards = relationship("Card", back_populates="deck", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True)
    page_id: Mapped[int | None] = mapped_column(ForeignKey("pages.id", ondelete="SET NULL"), nullable=True, index=True)
    block_id: Mapped[int | None] = mapped_column(ForeignKey("blocks.id", ondelete="SET NULL"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="basic")
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ease: Mapped[float] = mapped_column(Float, nullable=False, server_default="2.5")
    interval: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    repetition: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    due_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    deck = relationship("Deck", back_populates="cards")
    page = relationship("Page", back_populates="cards")
    block = relationship("Block", back_populates="cards")
    reviews = relationship("CardReview", back_populates="card", cascade="all, delete-orphan")


class CardReview(Base):
    __tablename__ = "card_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    ease: Mapped[float] = mapped_column(Float, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, nullable=False)
    repetition: Mapped[int] = mapped_column(Integer, nullable=False)
    due_at = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    card = relationship("Card", back_populates="reviews")
    user = relationship("User", back_populates="card_reviews")

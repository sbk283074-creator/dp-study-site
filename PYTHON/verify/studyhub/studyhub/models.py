from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from studyhub.timeutils import utcnow


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=utcnow, onupdate=utcnow, nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    decks: Mapped[list["Deck"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    review_logs: Mapped[list["ReviewLog"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Deck(TimestampMixin, Base):
    __tablename__ = "decks"
    __table_args__ = (Index("ix_decks_public_created", "is_public", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cloned_from_id: Mapped[int | None] = mapped_column(
        ForeignKey("decks.id", ondelete="SET NULL"), nullable=True
    )

    owner: Mapped["User"] = relationship(back_populates="decks")
    cards: Mapped[list["Card"]] = relationship(
        back_populates="deck", cascade="all, delete-orphan"
    )


class Card(TimestampMixin, Base):
    """One flashcard plus its scheduling state (see Decision 1)."""

    __tablename__ = "cards"
    __table_args__ = (Index("ix_cards_deck_due", "deck_id", "due_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id", ondelete="CASCADE"), nullable=False)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # --- scheduling state ---
    state: Mapped[str] = mapped_column(String(16), default="new", nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(), default=utcnow, index=True, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    deck: Mapped["Deck"] = relationship(back_populates="cards")


class ReviewLog(TimestampMixin, Base):
    """Append-only history of a single grade (see Decision 2)."""

    __tablename__ = "review_logs"
    __table_args__ = (
        Index("ix_review_logs_user_day", "user_id", "local_day"),
        Index("ix_review_logs_card_reviewed", "card_id", "reviewed_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[int | None] = mapped_column(
        ForeignKey("cards.id", ondelete="SET NULL"), nullable=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..4
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(), default=utcnow, nullable=False)
    local_day: Mapped[str] = mapped_column(String(10), index=True, nullable=False)

    interval_before: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    interval_after: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ease_before: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    ease_after: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="review_logs")

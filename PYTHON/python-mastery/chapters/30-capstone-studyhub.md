---
chapter: 30
part: 4
title: CAPSTONE A: StudyHub — A Full-Stack Application
summary: Build, test, and ship StudyHub, a multi-user spaced-repetition app with FastAPI, SQLAlchemy 2.x, HTMX, Alembic, and Docker.
minutes: 180
tags: [fastapi, sqlalchemy, htmx, alembic, docker, testing, capstone]
---

You are going to build a real product: StudyHub, a multi-user spaced-repetition study platform.
Users register, build decks of flashcards, and review them on a schedule computed by a real
scheduling algorithm. They get a stats dashboard with streaks and retention. They can publish
decks, clone other people's decks, and import/export their own as JSON or CSV. It runs in Docker
against Postgres and has a test suite that covers the scheduler, the services, and the HTTP
layer. This is the right capstone because it touches every single skill from Track A at once:
Pydantic models at the edges, SQLAlchemy models in the middle, a pure-Python core that holds the
actual business logic, FastAPI routers with dependencies and auth, Jinja2 plus HTMX for the UI,
Alembic for schema changes, and Docker plus CI to ship it. Nothing here is a toy. Every file
below is a file you would write at work.

## What you are building

Four screens. Build towards them: every milestone below exists to make one of them real, and
"does this move me closer to the screenshot?" is a good test for whether a task is worth doing.

![Sign-in. Sessions survive a browser restart, so the cookie is set server-side and http-only.](figures/studyhub-login.svg)

The deck list is the home screen. The number that matters is the due count on the right — it is
computed by the scheduler from Milestone 1, not stored.

![The deck list. Each row shows total cards, new cards, and how many are due right now.](figures/studyhub-dashboard.svg)

The review screen is the whole product in one view. HTMX swaps the card in place, so grading a
card never reloads the page.

![The review screen: question, revealed answer, and four grades with the interval each one schedules.](figures/studyhub-review.svg)

The stats dashboard is where the append-only review log pays off — retention and streaks are
queries over history you decided to keep.

![Stats: three headline metrics, a 14-day review histogram, and an activity heatmap.](figures/studyhub-stats.svg)

## The spec

Write the spec before the code. A capstone without a spec becomes a capstone that is 80% done
forever, because you keep discovering new requirements instead of finishing old ones.

User stories:

- [ ] As a visitor, I can register with an email, display name, and password (minimum 8 chars).
- [ ] As a user, I can log in and log out, and my session survives a browser restart.
- [ ] As a user, my password is never stored or logged in plaintext.
- [ ] As a user, I can create a deck with a title and description.
- [ ] As a user, I can add cards (front/back) to a deck and edit or delete them.
- [ ] As a user, I can start a review session on a deck and see only cards that are due.
- [ ] As a user, I grade each card Again / Hard / Good / Easy and immediately see the next card,
      without a full page reload.
- [ ] As a user, the next due date for a card is computed by the scheduler and persisted.
- [ ] As a user, I can see a dashboard: cards due today, retention over 30 days, my streak, and
      a bar chart of reviews per day for the last 30 days.
- [ ] As a user, I can publish a deck so others can find it.
- [ ] As a user, I can browse public decks and clone one into my own account.
- [ ] As a user, I can export a deck as JSON or CSV and import one back.
- [ ] As an operator, I can run the app in Docker with Postgres and apply migrations on deploy.

Non-goals — say these out loud so you do not accidentally build them:

- No mobile app, no native client. The web UI is responsive; that is enough.
- No images or audio on cards in v1. Text only. (It is extension #3 below for a reason.)
- No real-time collaboration, no comments, no ratings on public decks.
- No email verification or password reset. Out of scope for a self-hosted v1.
- No JavaScript build step. HTMX from a CDN plus one CSS file. No npm, no bundler, no webpack.
- No "optimize the scheduler with machine learning". Simplified SM-2 is the algorithm. Ship it.

:::tip Write the non-goals down where you can see them
The most common way a capstone dies is scope creep disguised as quality. Every time you think
"but it would be better if...", check the non-goals list. If it is on there, it goes in the
*"next version"* file, not in today's commit.
:::

## Data model

Four tables: `users`, `decks`, `cards`, `review_logs`. The interesting part is not the tables,
it is the two decisions behind them.

**Decision 1 — scheduling state lives on the card.** A card stores `ease_factor`,
`interval_days`, `repetitions`, `lapses`, `due_at`, and `state`. The alternative is to compute
those on the fly by replaying the review history. Replaying is "purer" in some abstract sense
and it is a trap: every query that wants to know *what is due right now* would have to fold an
entire card history first, so "give me 20 due cards" becomes "load everything and compute in
Python". You cannot index a value you do not store. Write the result of the computation to the
row, keep the history for auditing and analytics, and make the scheduler a pure function so the
write is trivially testable. Storage is cheap; a full-table scan per page load is not.

**Decision 2 — review logs are append-only.** `ReviewLog` rows are never updated or deleted.
They are the audit trail: they let you recompute stats, debug "why is this card due in 2027?",
and — critically — let you change the scheduler later and backfill without destroying history.
Note the deliberate asymmetry: `cards` cascade-deletes from decks, but `review_logs.card_id`
uses `ondelete="SET NULL"`. Delete a card and its history survives as orphaned rows. That is
intentional. Your retention chart should not change because someone tidied up a deck.

```python
# studyhub/models.py
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
```

```python
# studyhub/timeutils.py
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc


def utcnow() -> datetime:
    """Naive UTC timestamp. Every DateTime column in this app stores this."""
    return datetime.now(UTC).replace(tzinfo=None)


def local_day(moment: datetime, tz_name: str = "UTC") -> str:
    """The user's calendar day (YYYY-MM-DD) for a UTC timestamp."""
    aware = moment.replace(tzinfo=UTC)
    return aware.astimezone(ZoneInfo(tz_name)).date().isoformat()


def end_of_local_day(moment: datetime, tz_name: str) -> datetime:
    """UTC instant corresponding to 23:59:59.999999 in the user's timezone."""
    local = moment.replace(tzinfo=UTC).astimezone(ZoneInfo(tz_name))
    midnight_tomorrow = (local + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return midnight_tomorrow.astimezone(UTC).replace(tzinfo=None)


def last_n_days(today: str, count: int) -> list[str]:
    end = date.fromisoformat(today)
    return [(end - timedelta(days=offset)).isoformat() for offset in range(count - 1, -1, -1)]
```

:::pitfall Naive UTC or aware UTC — pick one and never mix
These columns store **naive** UTC (`datetime.now(UTC).replace(tzinfo=None)`). If you ever write
`datetime.now()` into a `due_at` column you have silently stored *server local time* in a field
the whole app reads as UTC, and every due date on the box is off by the server's offset. This bug
does not raise; it just quietly schedules cards wrongly. One helper (`utcnow`) used everywhere is
the entire defence.
:::

## Project layout

```text
studyhub/
├── pyproject.toml
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 2026_03_01_1200-8f1c2a4b9d10_initial_schema.py
├── studyhub/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── errors.py
│   ├── security.py
│   ├── scheduler.py          # pure core, no DB
│   ├── timeutils.py
│   ├── io_utils.py           # import / export
│   ├── repositories.py       # SQL only
│   ├── services.py           # business rules, transactions
│   ├── deps.py               # FastAPI dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cards.py
│   │   ├── decks.py
│   │   ├── io.py
│   │   ├── pages.py
│   │   ├── review.py
│   │   └── stats.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── landing.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── decks.html
│   │   ├── deck_detail.html
│   │   ├── review.html
│   │   ├── _review_card.html
│   │   ├── browse.html
│   │   └── stats.html
│   └── static/
│       └── app.css
└── tests/
    ├── conftest.py
    ├── test_scheduler.py
    ├── test_services.py
    ├── test_auth_api.py
    └── test_review_flow.py
```

The split that matters is `scheduler.py` (no imports from SQLAlchemy at all), `repositories.py`
(SQL, no business rules), and `services.py` (business rules, uses repositories, owns the
transaction). Everything else is plumbing around those three.

## Milestone 1: the scheduler (pure core)

The scheduler is the only genuinely novel logic in this app, and it is the one thing you must be
able to reason about with total confidence. So it gets no database, no clock, and no framework.
It is a frozen dataclass in, a frozen dataclass out, with `now` passed as an argument. That means
tests run in microseconds and never need a fixture, and "what happens if I grade Easy twice?"
is a question you can answer in a REPL.

Write the tests first. This is the whole point of a pure core: the tests are cheap enough that
you have no excuse.

```python
# tests/test_scheduler.py
from datetime import datetime

import pytest

from studyhub.scheduler import CardState, Rating, preview_intervals, schedule

T0 = datetime(2026, 3, 1, 9, 0)  # naive UTC, see timeutils.utcnow


def test_first_good_review_schedules_one_day():
    outcome = schedule(CardState(), Rating.GOOD, T0)
    assert outcome.interval_days == 1.0
    assert outcome.due_at == datetime(2026, 3, 2, 9, 0)


def test_second_good_review_schedules_six_days():
    state = CardState(interval_days=1.0, repetitions=1)
    outcome = schedule(state, Rating.GOOD, T0)
    assert outcome.interval_days == 6.0
    assert outcome.state.repetitions == 2


def test_mature_good_review_multiplies_by_ease():
    state = CardState(interval_days=6.0, repetitions=2, ease_factor=2.5)
    assert schedule(state, Rating.GOOD, T0).interval_days == 15.0


def test_easy_grows_faster_than_good():
    state = CardState(interval_days=6.0, repetitions=2, ease_factor=2.5)
    assert schedule(state, Rating.EASY, T0).interval_days == 19.5
    assert schedule(state, Rating.EASY, T0).state.ease_factor == 2.65


def test_hard_uses_the_1_2_multiplier():
    state = CardState(interval_days=6.0, repetitions=2, ease_factor=2.5)
    assert schedule(state, Rating.HARD, T0).interval_days == 7.2
    assert schedule(state, Rating.HARD, T0).state.ease_factor == 2.35


def test_again_resets_repetitions_and_counts_a_lapse():
    state = CardState(interval_days=15.0, repetitions=4, lapses=1, ease_factor=2.5)
    outcome = schedule(state, Rating.AGAIN, T0)
    assert outcome.state.repetitions == 0
    assert outcome.state.lapses == 2
    assert outcome.state.interval_days == 0.0
    assert outcome.state.ease_factor == 2.3
    assert outcome.due_at == T0.replace(minute=10)  # back in 10 minutes


def test_ease_never_falls_below_the_floor():
    state = CardState(ease_factor=1.3)
    for _ in range(50):
        state = schedule(state, Rating.AGAIN, T0).state
    assert state.ease_factor == 1.3


def test_interval_is_capped():
    state = CardState(interval_days=3000.0, repetitions=12, ease_factor=2.5)
    assert schedule(state, Rating.EASY, T0).interval_days == 3650.0


def test_scheduling_is_pure():
    state = CardState(interval_days=6.0, repetitions=2)
    before = (state.ease_factor, state.interval_days, state.repetitions, state.lapses)
    schedule(state, Rating.EASY, T0)
    assert (state.ease_factor, state.interval_days, state.repetitions, state.lapses) == before


def test_preview_matches_what_grading_would_do():
    state = CardState(interval_days=6.0, repetitions=2, ease_factor=2.5)
    preview = preview_intervals(state, T0)
    assert preview["good"] == "15d"
    assert schedule(state, Rating.GOOD, T0).interval_days == 15.0


@pytest.mark.parametrize("rating", [1, 2, 3, 4])
def test_every_rating_produces_a_future_due_date(rating):
    outcome = schedule(CardState(interval_days=3.0, repetitions=2), Rating(rating), T0)
    assert outcome.due_at > T0
```

Now the implementation. It is a simplified SM-2: track ease, interval, and repetition count;
adjust ease on every grade; grow the interval multiplicatively once the card is mature.

```python
# studyhub/scheduler.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import IntEnum


class Rating(IntEnum):
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


MIN_EASE = 1.3
MAX_EASE = 2.8
MAX_INTERVAL_DAYS = 3650.0
AGAIN_DELAY = timedelta(minutes=10)
FIRST_INTERVAL = 1.0
SECOND_INTERVAL = 6.0
EASY_FIRST_INTERVAL = 4.0
HARD_MULTIPLIER = 1.2
EASY_BONUS = 1.3

EASE_DELTA = {
    Rating.AGAIN: -0.20,
    Rating.HARD: -0.15,
    Rating.GOOD: 0.0,
    Rating.EASY: +0.15,
}


@dataclass(frozen=True, slots=True)
class CardState:
    ease_factor: float = 2.5
    interval_days: float = 0.0
    repetitions: int = 0
    lapses: int = 0


@dataclass(frozen=True, slots=True)
class ReviewOutcome:
    state: CardState
    due_at: datetime
    interval_days: float
    rating: Rating


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _next_interval(state: CardState, ease: float, rating: Rating) -> float:
    if state.repetitions == 0:
        base = EASY_FIRST_INTERVAL if rating is Rating.EASY else FIRST_INTERVAL
    elif state.repetitions == 1:
        base = SECOND_INTERVAL
        if rating is Rating.HARD:
            base *= HARD_MULTIPLIER
        elif rating is Rating.EASY:
            base *= EASY_BONUS
    elif rating is Rating.HARD:
        base = state.interval_days * HARD_MULTIPLIER
    elif rating is Rating.EASY:
        base = state.interval_days * ease * EASY_BONUS
    else:  # Rating.GOOD
        base = state.interval_days * ease
    return round(_clamp(base, 1.0, MAX_INTERVAL_DAYS), 2)


def schedule(state: CardState, rating: Rating, now: datetime) -> ReviewOutcome:
    """Pure: given current state and a grade, return the new state and due date."""
    rating = Rating(rating)
    ease = _clamp(state.ease_factor + EASE_DELTA[rating], MIN_EASE, MAX_EASE)

    if rating is Rating.AGAIN:
        new_state = CardState(
            ease_factor=ease,
            interval_days=0.0,
            repetitions=0,
            lapses=state.lapses + 1,
        )
        return ReviewOutcome(new_state, now + AGAIN_DELAY, 0.0, rating)

    interval = _next_interval(state, ease, rating)
    new_state = CardState(
        ease_factor=ease,
        interval_days=interval,
        repetitions=state.repetitions + 1,
        lapses=state.lapses,
    )
    return ReviewOutcome(new_state, now + timedelta(days=interval), interval, rating)


def humanize(delta: timedelta) -> str:
    total_minutes = int(delta.total_seconds() // 60)
    if total_minutes < 60:
        return f"{total_minutes}m"
    if total_minutes < 60 * 24:
        return f"{total_minutes // 60}h"
    days = total_minutes // (60 * 24)
    if days < 30:
        return f"{days}d"
    if days < 365:
        return f"{days / 30:.1f}mo"
    return f"{days / 365:.1f}y"


def preview_intervals(state: CardState, now: datetime) -> dict[str, str]:
    """What each button would do — shown on the review screen."""
    return {
        name.lower(): humanize(schedule(state, Rating[name.upper()], now).due_at - now)
        for name in ("again", "hard", "good", "easy")
    }
```

```bash
python3 -m pytest tests/test_scheduler.py -q
```

```text
14 passed in 0.08s
```

Fourteen tests, 0.08 seconds, no database, no fixtures. That is the payoff for keeping the core
pure. Anything you cannot test this cheaply is a thing you will not test.

## Milestone 2: persistence layer

Repositories own SQL. Services own transactions and rules. Routers own HTTP. When a query is
slow you open `repositories.py`; when a rule is wrong you open `services.py`; when a status code
is wrong you open a router. Never all three for one bug.

```python
# studyhub/config.py
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STUDYHUB_", env_file=".env")

    database_url: str = "sqlite+pysqlite:///./studyhub.db"
    secret_key: str = "dev-only-insecure-secret"
    session_cookie_name: str = "studyhub_session"
    session_ttl_seconds: int = 60 * 60 * 24 * 30
    cookie_secure: bool = False  # True behind HTTPS in production
    new_cards_per_day: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```python
# studyhub/db.py
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from studyhub.config import get_settings


def _connect_args(url: str) -> dict:
    return {"check_same_thread": False} if url.startswith("sqlite") else {}


settings = get_settings()
engine = create_engine(settings.database_url, connect_args=_connect_args(settings.database_url), future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
```

`expire_on_commit=False` is deliberate: after `commit()` you can still read `card.due_at`
without triggering a fresh SELECT. Without it, every attribute access after a commit issues
another query, and in a loop that is hundreds of round trips. You give up automatic refresh,
which is fine because you are about to return a Pydantic model anyway.

```python
# studyhub/repositories.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from studyhub.models import Card, Deck, ReviewLog, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email.lower()))

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user


class DeckRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_for_user_with_counts(self, owner_id: int) -> list[tuple[Deck, int]]:
        count = (
            select(func.count(Card.id))
            .where(Card.deck_id == Deck.id)
            .scalar_subquery()
        )
        rows = self.session.execute(
            select(Deck, count)
            .where(Deck.owner_id == owner_id)
            .order_by(Deck.created_at.desc())
        ).all()
        return list(rows)

    def public_decks(self, limit: int = 50) -> list[tuple[Deck, int]]:
        count = (
            select(func.count(Card.id))
            .where(Card.deck_id == Deck.id)
            .scalar_subquery()
        )
        rows = self.session.execute(
            select(Deck, count)
            .where(Deck.is_public.is_(True))
            .order_by(Deck.created_at.desc())
            .limit(limit)
        ).all()
        return list(rows)

    def get(self, deck_id: int) -> Deck | None:
        return self.session.get(Deck, deck_id)

    def add(self, deck: Deck) -> Deck:
        self.session.add(deck)
        self.session.flush()
        return deck

    def delete(self, deck: Deck) -> None:
        self.session.delete(deck)


class CardRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def due(self, owner_id: int, deck_id: int | None, now: datetime, limit: int) -> list[Card]:
        stmt = (
            select(Card)
            .join(Deck, Card.deck_id == Deck.id)
            .where(Deck.owner_id == owner_id, Card.due_at <= now)
            .order_by(Card.due_at)
            .limit(limit)
        )
        if deck_id is not None:
            stmt = stmt.where(Card.deck_id == deck_id)
        return list(self.session.scalars(stmt))

    def due_count(self, owner_id: int, deck_id: int | None, now: datetime) -> int:
        stmt = (
            select(func.count(Card.id))
            .join(Deck, Card.deck_id == Deck.id)
            .where(Deck.owner_id == owner_id, Card.due_at <= now)
        )
        if deck_id is not None:
            stmt = stmt.where(Card.deck_id == deck_id)
        return int(self.session.scalar(stmt) or 0)

    def get_for_owner(self, card_id: int, owner_id: int) -> Card | None:
        return self.session.scalar(
            select(Card).join(Deck).where(Card.id == card_id, Deck.owner_id == owner_id)
        )

    def add(self, card: Card) -> Card:
        self.session.add(card)
        self.session.flush()
        return card


class ReviewLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, log: ReviewLog) -> ReviewLog:
        self.session.add(log)
        self.session.flush()
        return log

    def daily_counts(self, user_id: int, start_day: str) -> list[tuple[str, int, int]]:
        rows = self.session.execute(
            select(
                ReviewLog.local_day,
                func.count(ReviewLog.id).label("reviews"),
                func.sum(func.iif(ReviewLog.rating > 1, 1, 0)).label("remembered"),
            )
            .where(ReviewLog.user_id == user_id, ReviewLog.local_day >= start_day)
            .group_by(ReviewLog.local_day)
        ).all()
        return [(day, int(reviews), int(remembered or 0)) for day, reviews, remembered in rows]

    def distinct_days(self, user_id: int) -> set[str]:
        rows = self.session.scalars(
            select(ReviewLog.local_day).where(ReviewLog.user_id == user_id).distinct()
        ).all()
        return set(rows)
```

:::note `func.iif` and portability
`func.iif` is SQLite-specific. On Postgres use `func.sum(cast(ReviewLog.rating > 1, Integer))`
or a `case()` expression. If you want one code path for both, use
`from sqlalchemy import case, cast, Integer` and write
`func.sum(case((ReviewLog.rating > 1, 1), else_=0))` — SQLAlchemy renders it correctly on both
dialects. Do this before you deploy, not after.
:::

Services wrap the repositories with rules and own `commit()`:

```python
# studyhub/services.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from studyhub import timeutils
from studyhub.errors import BadCredentialsError, DuplicateEmailError, ForbiddenError, NotFoundError
from studyhub.models import Card, Deck, ReviewLog, User
from studyhub.repositories import (
    CardRepository,
    DeckRepository,
    ReviewLogRepository,
    UserRepository,
)
from studyhub.scheduler import CardState, Rating, ReviewOutcome, schedule
from studyhub.security import hash_password, verify_password


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def register(self, email: str, display_name: str, password: str) -> User:
        email = email.strip().lower()
        if self.users.get_by_email(email) is not None:
            raise DuplicateEmailError("That email is already registered.")
        user = User(
            email=email,
            display_name=display_name.strip(),
            password_hash=hash_password(password),
        )
        self.users.add(user)
        self.session.commit()
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email.strip().lower())
        # Always run a hash comparison so timing does not reveal account existence.
        if user is None or not verify_password(password, user.password_hash):
            raise BadCredentialsError("Invalid email or password.")
        if not user.is_active:
            raise ForbiddenError("This account is disabled.")
        self.session.commit()
        return user


class DeckService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.decks = DeckRepository(session)
        self.cards = CardRepository(session)

    def create(self, owner: User, title: str, description: str = "", is_public: bool = False) -> Deck:
        deck = Deck(owner_id=owner.id, title=title.strip(), description=description, is_public=is_public)
        self.decks.add(deck)
        self.session.commit()
        return deck

    def list_for(self, owner_id: int) -> list[tuple[Deck, int]]:
        return self.decks.list_for_user_with_counts(owner_id)

    def require_owned(self, deck_id: int, owner_id: int) -> Deck:
        deck = self.decks.get(deck_id)
        if deck is None:
            raise NotFoundError("Deck not found.")
        if deck.owner_id != owner_id:
            raise ForbiddenError("That deck belongs to someone else.")
        return deck

    def publish(self, deck_id: int, owner_id: int, is_public: bool) -> Deck:
        deck = self.require_owned(deck_id, owner_id)
        deck.is_public = is_public
        self.session.commit()
        return deck

    def add_card(self, deck_id: int, owner_id: int, front: str, back: str) -> Card:
        deck = self.require_owned(deck_id, owner_id)
        card = Card(deck_id=deck.id, front=front, back=back, position=len(deck.cards))
        self.cards.add(card)
        self.session.commit()
        return card

    def clone_public(self, deck_id: int, owner: User) -> Deck:
        source = self.decks.get(deck_id)
        if source is None or not source.is_public:
            raise NotFoundError("Public deck not found.")
        copy = Deck(
            owner_id=owner.id,
            title=f"{source.title} (copy)",
            description=source.description,
            is_public=False,
            cloned_from_id=source.id,
        )
        self.decks.add(copy)
        for original in source.cards:
            self.cards.add(Card(deck_id=copy.id, front=original.front, back=original.back, position=original.position))
        self.session.commit()
        return copy


class ReviewService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.cards = CardRepository(session)
        self.logs = ReviewLogRepository(session)

    def due(self, user_id: int, deck_id: int | None = None, limit: int = 20) -> list[Card]:
        return self.cards.due(user_id, deck_id, timeutils.utcnow(), limit)

    def due_count(self, user_id: int, deck_id: int | None = None) -> int:
        return self.cards.due_count(user_id, deck_id, timeutils.utcnow())

    def grade(
        self, user: User, card_id: int, rating: int, duration_ms: int = 0
    ) -> tuple[Card, ReviewOutcome]:
        card = self.cards.get_for_owner(card_id, user.id)
        if card is None:
            raise NotFoundError("Card not found.")
        rating = Rating(rating)
        now = timeutils.utcnow()
        before = CardState(card.ease_factor, card.interval_days, card.repetitions, card.lapses)
        outcome = schedule(before, rating, now)

        self.logs.add(
            ReviewLog(
                user_id=user.id,
                card_id=card.id,
                rating=int(rating),
                reviewed_at=now,
                local_day=timeutils.local_day(now, user.timezone),
                interval_before=before.interval_days,
                interval_after=outcome.interval_days,
                ease_before=before.ease_factor,
                ease_after=outcome.state.ease_factor,
                duration_ms=duration_ms,
            )
        )
        card.state = "learning" if rating is Rating.AGAIN else "review"
        card.due_at = outcome.due_at
        card.ease_factor = outcome.state.ease_factor
        card.interval_days = outcome.state.interval_days
        card.repetitions = outcome.state.repetitions
        card.lapses = outcome.state.lapses
        card.last_reviewed_at = now
        self.session.commit()
        return card, outcome
```

`grade()` does five things in one transaction: load, compute with the pure scheduler, append a
log, write the new state, commit. If any of it fails, Postgres rolls back all of it and you never
get a card whose state disagrees with its history.

Alembic migration:

```bash
python3 -m alembic revision --autogenerate -m "initial schema"
```

```python
# alembic/versions/2026_03_01_1200-8f1c2a4b9d10_initial_schema.py
def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False, server_default="UTC"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "decks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("cloned_from_id", sa.Integer(), sa.ForeignKey("decks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_decks_owner_id", "decks", ["owner_id"])
    op.create_index("ix_decks_public_created", "decks", ["is_public", "created_at"])

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("deck_id", sa.Integer(), sa.ForeignKey("decks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("state", sa.String(length=16), nullable=False, server_default="new"),
        sa.Column("due_at", sa.DateTime(), nullable=False),
        sa.Column("ease_factor", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("interval_days", sa.Float(), nullable=False, server_default="0"),
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lapses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    # The one index that matters: "what is due, in this deck, soonest first".
    op.create_index("ix_cards_deck_due", "cards", ["deck_id", "due_at"])
    op.create_index("ix_cards_due_at", "cards", ["due_at"])

    op.create_table(
        "review_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("card_id", sa.Integer(), sa.ForeignKey("cards.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(), nullable=False),
        sa.Column("local_day", sa.String(length=10), nullable=False),
        sa.Column("interval_before", sa.Float(), nullable=False, server_default="0"),
        sa.Column("interval_after", sa.Float(), nullable=False, server_default="0"),
        sa.Column("ease_before", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("ease_after", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_review_logs_user_day", "review_logs", ["user_id", "local_day"])
    op.create_index("ix_review_logs_card_reviewed", "review_logs", ["card_id", "reviewed_at"])
    op.create_index("ix_review_logs_local_day", "review_logs", ["local_day"])


def downgrade() -> None:
    op.drop_table("review_logs")
    op.drop_table("cards")
    op.drop_table("decks")
    op.drop_table("users")
```

Point `alembic/env.py` at your settings so it does not carry a second copy of the URL:

```python
# alembic/env.py (key lines)
from studyhub.config import get_settings
from studyhub.models import Base

config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))
target_metadata = Base.metadata
```

:::pitfall Autogenerate is a draft, not a migration
`--autogenerate` misses things: server default changes, table renames it guesses as
drop-and-create, and CHECK constraints on SQLite. Read every generated migration before you run
it. The one it will get wrong here is a column rename — it will happily emit `drop_column` +
`add_column`, which destroys data. Use `op.alter_column(..., new_column_name=...)` instead.
:::

## Milestone 3: the API

Schemas at the edge, dependencies in the middle, routers that do nothing but translate.

Domain errors get their own module so that `services.py` never imports `fastapi`. Services raise,
the app decides what that means in HTTP.

```python
# studyhub/errors.py
from __future__ import annotations


class AppError(Exception):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class ForbiddenError(AppError):
    status_code = 403


class DuplicateEmailError(AppError):
    status_code = 409


class BadCredentialsError(AppError):
    status_code = 401
```

```python
# studyhub/schemas.py
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str
    timezone: str


class DeckCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    is_public: bool = False


class DeckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    description: str
    is_public: bool
    card_count: int = 0
    created_at: datetime


class CardCreate(BaseModel):
    front: str = Field(min_length=1)
    back: str = Field(min_length=1)


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    deck_id: int
    front: str
    back: str
    state: str
    due_at: datetime
    ease_factor: float
    interval_days: float
    repetitions: int
    lapses: int


class ReviewAnswer(BaseModel):
    rating: int = Field(ge=1, le=4)
    duration_ms: int = Field(default=0, ge=0)


class ReviewResult(BaseModel):
    card_id: int
    rating: int
    interval_days: float
    due_at: datetime
    ease_factor: float
    repetitions: int
    lapses: int
    remaining_due: int


class DailyPoint(BaseModel):
    day: str
    reviews: int
    remembered: int


class StatsSummary(BaseModel):
    due_today: int
    reviews_today: int
    new_cards: int
    total_cards: int
    retention_30d: float  # percentage, 0.0 - 100.0
    streak_days: int


class CardPair(BaseModel):
    front: str
    back: str


class DeckExport(BaseModel):
    version: int = 1
    title: str
    description: str = ""
    cards: list[CardPair] = Field(default_factory=list)


class DeckImport(BaseModel):
    format: str = Field(pattern="^(json|csv)$")
    content: str = Field(min_length=1)
    title: str | None = None
```

Security and dependencies:

```python
# studyhub/security.py
from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext

_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_context.verify(password, password_hash)


def create_session_token(secret_key: str, user_id: int) -> str:
    return URLSafeTimedSerializer(secret_key).dumps({"uid": user_id})


def read_session_token(secret_key: str, token: str, max_age: int) -> int | None:
    try:
        data = URLSafeTimedSerializer(secret_key).loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return int(data["uid"])
```

```python
# studyhub/deps.py
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from studyhub.config import Settings, get_settings
from studyhub.db import get_session
from studyhub.models import User
from studyhub.repositories import UserRepository
from studyhub.security import read_session_token
from studyhub.services import AuthService, DeckService, ReviewService, StatsService

CurrentSession = Annotated[Session, Depends(get_session)]
CurrentSettings = Annotated[Settings, Depends(get_settings)]


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def current_user(
    request: Request,
    session: CurrentSession,
    settings: CurrentSettings,
) -> User:
    """API dependency: 401 as JSON when not authenticated."""
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = read_session_token(settings.secret_key, token, settings.session_ttl_seconds)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = UserRepository(session).get(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def current_user_page(
    request: Request,
    session: CurrentSession,
    settings: CurrentSettings,
) -> User:
    """Page dependency: 307 to /login instead of a JSON 401."""
    try:
        return current_user(request, session, settings)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/login"},
            detail="Not authenticated",
        ) from None


CurrentUser = Annotated[User, Depends(current_user)]
PageUser = Annotated[User, Depends(current_user_page)]
Templates = Annotated[Jinja2Templates, Depends(get_templates)]


def get_auth_service(session: CurrentSession) -> AuthService:
    return AuthService(session)


def get_deck_service(session: CurrentSession) -> DeckService:
    return DeckService(session)


def get_review_service(session: CurrentSession) -> ReviewService:
    return ReviewService(session)


def get_stats_service(session: CurrentSession) -> StatsService:
    return StatsService(session)
```

:::tip The 307 trick
A dependency cannot return a `RedirectResponse`, but it *can* raise an `HTTPException` with a
`Location` header. FastAPI's handler turns that into a real redirect. One dependency, two
behaviours: JSON 401 for `/api/*`, redirect for pages.
:::

The auth router:

```python
# studyhub/routers/auth.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from studyhub.config import Settings
from studyhub.deps import CurrentSettings, CurrentUser, get_auth_service
from studyhub.errors import BadCredentialsError, DuplicateEmailError, ForbiddenError
from studyhub.schemas import LoginRequest, UserCreate, UserRead
from studyhub.security import create_session_token
from studyhub.services import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, settings: Settings, user_id: int) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(settings.secret_key, user_id),
        max_age=settings.session_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    response: Response,
    settings: CurrentSettings,
    auth: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        user = auth.register(
            email=payload.email, display_name=payload.display_name, password=payload.password
        )
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    _set_session_cookie(response, settings, user.id)
    return UserRead.model_validate(user)


@router.post("/login", response_model=UserRead)
def login(
    payload: LoginRequest,
    response: Response,
    settings: CurrentSettings,
    auth: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        user = auth.authenticate(email=payload.email, password=payload.password)
    except BadCredentialsError as exc:
        # Same message for unknown email and wrong password: do not leak account existence.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        ) from exc
    except ForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    _set_session_cookie(response, settings, user.id)
    return UserRead.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, settings: CurrentSettings) -> Response:
    response.delete_cookie(settings.session_cookie_name)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
```

The review router — both the JSON API and the HTMX endpoint that returns an HTML fragment:

```python
# studyhub/routers/review.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Query

from studyhub.deps import CurrentUser, PageUser, Templates, get_review_service
from studyhub.errors import NotFoundError
from studyhub.schemas import CardRead, ReviewAnswer, ReviewResult
from studyhub.scheduler import CardState, preview_intervals
from studyhub.services import ReviewService
from studyhub.timeutils import utcnow

router = APIRouter(tags=["review"])


@router.get("/api/review/queue", response_model=list[CardRead])
def queue(
    user: CurrentUser,
    deck_id: int | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    review: ReviewService = Depends(get_review_service),
) -> list[CardRead]:
    cards = review.due(user.id, deck_id=deck_id, limit=limit)
    return [CardRead.model_validate(card) for card in cards]


@router.post("/api/review/{card_id}", response_model=ReviewResult)
def grade_card(
    card_id: int,
    payload: ReviewAnswer,
    user: CurrentUser,
    review: ReviewService = Depends(get_review_service),
) -> ReviewResult:
    try:
        card, outcome = review.grade(user, card_id, payload.rating, payload.duration_ms)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ReviewResult(
        card_id=card.id,
        rating=int(outcome.rating),
        interval_days=outcome.interval_days,
        due_at=card.due_at,
        ease_factor=card.ease_factor,
        repetitions=card.repetitions,
        lapses=card.lapses,
        remaining_due=review.due_count(user.id),
    )


@router.post("/review/{card_id}/answer")
def grade_card_html(
    card_id: int,
    request: Request,
    user: PageUser,
    templates: Templates,
    deck_id: int = Form(...),
    rating: int = Form(ge=1, le=4),
    review: ReviewService = Depends(get_review_service),
):
    try:
        review.grade(user, card_id, rating)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    next_cards = review.due(user.id, deck_id=deck_id, limit=5)
    next_card = next_cards[0] if next_cards else None
    if next_card is not None:
        state = CardState(
            next_card.ease_factor,
            next_card.interval_days,
            next_card.repetitions,
            next_card.lapses,
        )
        preview = preview_intervals(state, utcnow())
    else:
        preview = {}

    context = {
        "deck_id": deck_id,
        "card": next_card,
        "remaining": max(len(next_cards) - 1, 0),
        "preview": preview,
    }
    return templates.TemplateResponse(request=request, name="_review_card.html", context=context)
```

The router imports `Request` from `fastapi` alongside `Form`; add it to the import list at the
top of `review.py`.

Routers do no work of their own: read the form, call one service method, render a fragment. All
the interesting behaviour is either in the service or in the template.

The remaining routers are thin by comparison:

```python
# studyhub/routers/decks.py (abbreviated)
from fastapi import APIRouter, Depends, HTTPException, status

from studyhub.deps import CurrentUser, get_deck_service
from studyhub.errors import ForbiddenError, NotFoundError
from studyhub.schemas import CardCreate, CardRead, DeckCreate, DeckRead
from studyhub.services import DeckService

router = APIRouter(prefix="/api/decks", tags=["decks"])


@router.get("", response_model=list[DeckRead])
def list_decks(user: CurrentUser, decks: DeckService = Depends(get_deck_service)) -> list[DeckRead]:
    return [
        DeckRead(id=deck.id, owner_id=deck.owner_id, title=deck.title,
                 description=deck.description, is_public=deck.is_public,
                 card_count=count, created_at=deck.created_at)
        for deck, count in decks.list_for(user.id)
    ]


@router.post("", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(payload: DeckCreate, user: CurrentUser,
                decks: DeckService = Depends(get_deck_service)) -> DeckRead:
    deck = decks.create(user, payload.title, payload.description, payload.is_public)
    return DeckRead(id=deck.id, owner_id=deck.owner_id, title=deck.title,
                    description=deck.description, is_public=deck.is_public,
                    card_count=0, created_at=deck.created_at)


@router.post("/{deck_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def add_card(deck_id: int, payload: CardCreate, user: CurrentUser,
             decks: DeckService = Depends(get_deck_service)) -> CardRead:
    try:
        card = decks.add_card(deck_id, user.id, payload.front, payload.back)
    except (NotFoundError, ForbiddenError) as exc:
        raise HTTPException(status_code=404 if isinstance(exc, NotFoundError) else 403,
                            detail=str(exc)) from exc
    return CardRead.model_validate(card)


@router.post("/{deck_id}/clone", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def clone_deck(deck_id: int, user: CurrentUser,
               decks: DeckService = Depends(get_deck_service)) -> DeckRead:
    try:
        copy = decks.clone_public(deck_id, user)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeckRead(id=copy.id, owner_id=copy.owner_id, title=copy.title,
                    description=copy.description, is_public=copy.is_public,
                    card_count=len(copy.cards), created_at=copy.created_at)
```

Import and export are pure data transformations, so they live in their own module with no
framework in sight. Add one method to `DeckService` first:

```python
# studyhub/services.py — add these to DeckService
# (plus `from studyhub.schemas import DeckExport` at the top of the file)

class DeckService:
    # ... the existing create() / get() / delete() methods ...

    def public(self, limit: int = 50) -> list[tuple[Deck, int]]:
        return self.decks.public_decks(limit)

    def import_deck(self, owner: User, export: DeckExport, title: str | None = None) -> Deck:
        deck = Deck(owner_id=owner.id, title=(title or export.title).strip(), description=export.description)
        self.decks.add(deck)
        for pair in export.cards:
            self.cards.add(Card(deck_id=deck.id, front=pair.front, back=pair.back))
        self.session.commit()
        return deck
```

```python
# studyhub/io_utils.py
from __future__ import annotations

import csv
import io as stdio

from studyhub.models import Deck
from studyhub.schemas import CardPair, DeckExport


def deck_to_export(deck: Deck) -> DeckExport:
    cards = sorted(deck.cards, key=lambda card: card.position)
    return DeckExport(
        title=deck.title,
        description=deck.description,
        cards=[CardPair(front=card.front, back=card.back) for card in cards],
    )


def to_json(deck: Deck) -> str:
    return deck_to_export(deck).model_dump_json(indent=2)


def to_csv(deck: Deck) -> str:
    buffer = stdio.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["front", "back"])
    for pair in deck_to_export(deck).cards:
        writer.writerow([pair.front, pair.back])
    return buffer.getvalue()


def parse_json(text: str) -> DeckExport:
    return DeckExport.model_validate_json(text)


def parse_csv(text: str, title: str = "Imported deck") -> DeckExport:
    reader = csv.DictReader(stdio.StringIO(text))
    columns = set(reader.fieldnames or [])
    if not {"front", "back"} <= columns:
        raise ValueError("CSV must have 'front' and 'back' columns")
    return DeckExport(
        title=title,
        cards=[CardPair(front=row["front"], back=row["back"]) for row in reader],
    )
```

```python
# studyhub/routers/io.py
from __future__ import annotations

import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from studyhub import io_utils
from studyhub.deps import CurrentUser, get_deck_service
from studyhub.errors import AppError
from studyhub.schemas import DeckImport, DeckRead
from studyhub.services import DeckService

router = APIRouter(prefix="/api/decks", tags=["import-export"])


def _slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "deck"


@router.get("/{deck_id}/export")
def export_deck(
    deck_id: int,
    format: Literal["json", "csv"] = Query(default="json"),
    user: CurrentUser = None,
    decks: DeckService = Depends(get_deck_service),
) -> Response:
    try:
        deck = decks.require_owned(deck_id, user.id)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    slug = _slugify(deck.title)
    if format == "json":
        body, media_type, extension = io_utils.to_json(deck), "application/json", "json"
    else:
        body, media_type, extension = io_utils.to_csv(deck), "text/csv", "csv"
    return Response(
        content=body,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{slug}.{extension}"'},
    )


@router.post("/import", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def import_deck(
    payload: DeckImport,
    user: CurrentUser = None,
    decks: DeckService = Depends(get_deck_service),
) -> DeckRead:
    try:
        export = (
            io_utils.parse_json(payload.content)
            if payload.format == "json"
            else io_utils.parse_csv(payload.content, payload.title or "Imported deck")
        )
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse deck: {exc}") from exc

    deck = decks.import_deck(user, export, payload.title)
    return DeckRead(id=deck.id, owner_id=deck.owner_id, title=deck.title,
                    description=deck.description, is_public=deck.is_public,
                    card_count=len(export.cards), created_at=deck.created_at)
```

`user: CurrentUser = None` is legal because `CurrentUser` is an `Annotated` alias carrying
`Depends`; the default is never used. Write it as `user: CurrentUser,` if your linter objects.

The stats router is two lines of work because the aggregation already lives in the service:

```python
# studyhub/routers/stats.py
from __future__ import annotations

from fastapi import APIRouter, Depends

from studyhub.deps import CurrentUser, get_stats_service
from studyhub.schemas import DailyPoint, StatsSummary
from studyhub.services import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=StatsSummary)
def summary(user: CurrentUser, stats: StatsService = Depends(get_stats_service)) -> StatsSummary:
    return stats.summary(user)


@router.get("/daily", response_model=list[DailyPoint])
def daily(user: CurrentUser, stats: StatsService = Depends(get_stats_service)) -> list[DailyPoint]:
    return stats.daily(user)
```

Finally the page routes. They are HTML-only: form in, redirect or template out. Add one more
dependency first:

```python
# studyhub/deps.py — add
def optional_user(
    request: Request,
    session: CurrentSession,
    settings: CurrentSettings,
) -> User | None:
    try:
        return current_user(request, session, settings)
    except HTTPException:
        return None


OptionalUser = Annotated[User | None, Depends(optional_user)]
```

```python
# studyhub/routers/pages.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from studyhub.deps import (
    CurrentSettings,
    OptionalUser,
    PageUser,
    Templates,
    get_auth_service,
    get_deck_service,
    get_stats_service,
)
from studyhub.errors import AppError, BadCredentialsError, DuplicateEmailError
from studyhub.services import AuthService, DeckService, StatsService

router = APIRouter(tags=["pages"])

SEE_OTHER = 303


def render(request: Request, templates: Templates, name: str, **context) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name=name, context=context)


@router.get("/", response_class=HTMLResponse)
def landing(request: Request, user: OptionalUser, templates: Templates) -> HTMLResponse:
    if user is not None:
        return RedirectResponse(url="/decks", status_code=SEE_OTHER)
    return render(request, templates, "landing.html", current_user=None)


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request, user: OptionalUser, templates: Templates) -> HTMLResponse:
    if user is not None:
        return RedirectResponse(url="/decks", status_code=SEE_OTHER)
    return render(request, templates, "login.html", current_user=None, error=None)


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    settings: CurrentSettings = None,
    templates: Templates = None,
    auth: AuthService = Depends(get_auth_service),
) -> HTMLResponse:
    try:
        user = auth.authenticate(email, password)
    except (BadCredentialsError, AppError):
        return render(
            request, templates, "login.html",
            current_user=None, error="Invalid email or password.",
        )
    response = RedirectResponse(url="/decks", status_code=SEE_OTHER)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(settings.secret_key, user.id),
        max_age=settings.session_ttl_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return response


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    email: str = Form(...),
    display_name: str = Form(...),
    password: str = Form(min_length=8),
    settings: CurrentSettings = None,
    templates: Templates = None,
    auth: AuthService = Depends(get_auth_service),
) -> HTMLResponse:
    try:
        user = auth.register(email, display_name, password)
    except DuplicateEmailError:
        return render(
            request, templates, "register.html",
            current_user=None, error="That email is already registered.",
        )
    response = RedirectResponse(url="/decks", status_code=SEE_OTHER)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=create_session_token(settings.secret_key, user.id),
        max_age=settings.session_ttl_seconds,
        httponly=True, samesite="lax", secure=settings.cookie_secure,
    )
    return response


@router.post("/logout")
def logout(settings: CurrentSettings = None) -> RedirectResponse:
    response = RedirectResponse(url="/login", status_code=SEE_OTHER)
    response.delete_cookie(settings.session_cookie_name)
    return response


@router.get("/decks", response_class=HTMLResponse)
def deck_list(
    request: Request,
    user: PageUser,
    templates: Templates,
    decks: DeckService = Depends(get_deck_service),
) -> HTMLResponse:
    return render(request, templates, "decks.html", current_user=user, decks=decks.list_for(user.id))


@router.post("/decks")
def create_deck(
    title: str = Form(min_length=1, max_length=200),
    description: str = Form(default=""),
    user: PageUser = None,
    decks: DeckService = Depends(get_deck_service),
) -> RedirectResponse:
    deck = decks.create(user, title, description)
    return RedirectResponse(url=f"/decks/{deck.id}", status_code=SEE_OTHER)


@router.get("/decks/{deck_id}", response_class=HTMLResponse)
def deck_detail(
    request: Request,
    deck_id: int,
    user: PageUser,
    templates: Templates,
    decks: DeckService = Depends(get_deck_service),
) -> HTMLResponse:
    try:
        deck = decks.require_owned(deck_id, user.id)
    except AppError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return render(request, templates, "deck_detail.html", current_user=user, deck=deck)


@router.get("/decks/{deck_id}/review", response_class=HTMLResponse)
def review_screen(
    request: Request,
    deck_id: int,
    user: PageUser,
    templates: Templates,
    decks: DeckService = Depends(get_deck_service),
    review_service=Depends(get_review_service),
) -> HTMLResponse:
    deck = decks.require_owned(deck_id, user.id)
    due = review_service.due(user.id, deck_id=deck_id, limit=5)
    card = due[0] if due else None
    preview = (
        preview_intervals(
            CardState(card.ease_factor, card.interval_days, card.repetitions, card.lapses),
            utcnow(),
        )
        if card
        else {}
    )
    return render(
        request, templates, "review.html", current_user=user, deck=deck, deck_id=deck.id,
        card=card, remaining=max(len(due) - 1, 0), preview=preview,
    )


@router.get("/browse", response_class=HTMLResponse)
def browse(
    request: Request,
    user: PageUser,
    templates: Templates,
    decks: DeckService = Depends(get_deck_service),
) -> HTMLResponse:
    return render(request, templates, "browse.html", current_user=user, decks=decks.public())


@router.post("/browse/{deck_id}/clone")
def clone(
    deck_id: int,
    user: PageUser = None,
    decks: DeckService = Depends(get_deck_service),
) -> RedirectResponse:
    try:
        copy = decks.clone_public(deck_id, user)
    except AppError:
        return RedirectResponse(url="/browse", status_code=SEE_OTHER)
    return RedirectResponse(url=f"/decks/{copy.id}", status_code=SEE_OTHER)


@router.get("/stats", response_class=HTMLResponse)
def stats_page(
    request: Request,
    user: PageUser,
    templates: Templates,
    stats: StatsService = Depends(get_stats_service),
) -> HTMLResponse:
    return render(
        request, templates, "stats.html",
        current_user=user, stats=stats.summary(user), daily=stats.daily(user),
    )
```

Two imports to finish `pages.py`: `from studyhub.scheduler import CardState, preview_intervals`
and `from studyhub.security import create_session_token`, plus `get_review_service` in the
`deps` import list.

:::note Always redirect after a POST
Every handler that mutates state returns a 303 with a `Location`, never a template. That is the
POST/redirect/GET pattern, and it is why refreshing after "Create deck" does not re-submit the
form. Use 303 (See Other), not 302 — 303 explicitly tells the browser to follow up with `GET`.
:::

Wire the app together, including the exception handlers that turn domain errors into 404/403 and
HTML errors for pages:

```python
# studyhub/main.py
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from studyhub.errors import AppError, ForbiddenError, NotFoundError
from studyhub.routers import auth, cards, decks, io, pages, review, stats

BASE_DIR = Path(__file__).parent


def create_app() -> FastAPI:
    app = FastAPI(title="StudyHub", version="1.0.0")
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
    app.state.templates = Jinja2Templates(directory=BASE_DIR / "templates")

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(decks.router)
    app.include_router(cards.router)
    app.include_router(review.router)
    app.include_router(stats.router)
    app.include_router(io.router)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse | HTMLResponse:
        status_code = 404 if isinstance(exc, NotFoundError) else 403
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=status_code, content={"detail": str(exc)})
        return HTMLResponse(
            status_code=status_code,
            content=f"<h1>{status_code}</h1><p>{exc}</p><a href='/decks'>Back to decks</a>",
        )

    return app


app = create_app()
```

## Milestone 4: the UI

One base template, HTMX from a CDN, one stylesheet. The review screen is the only genuinely
interactive part, and HTMX handles it with a form post that swaps a single fragment.

```html
<!-- studyhub/templates/base.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}StudyHub{% endblock %}</title>
  <link rel="stylesheet" href="/static/app.css">
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">StudyHub</a>
    <nav>
      {% if current_user %}
        <a href="/decks">Decks</a>
        <a href="/browse">Browse</a>
        <a href="/stats">Stats</a>
        <form method="post" action="/logout" class="inline"><button>Log out</button></form>
      {% else %}
        <a href="/login">Log in</a>
        <a href="/register">Sign up</a>
      {% endif %}
    </nav>
  </header>

  <main class="container">
    {% if flash %}<p class="flash">{{ flash }}</p>{% endif %}
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

```html
<!-- studyhub/templates/review.html -->
{% extends "base.html" %}
{% block title %}Review · {{ deck.title }}{% endblock %}

{% block content %}
<section class="review">
  <header class="review-header">
    <h1>{{ deck.title }}</h1>
    <a class="muted" href="/decks/{{ deck.id }}">Back to deck</a>
  </header>

  <div id="review-pane">
    {% include "_review_card.html" %}
  </div>
</section>
{% endblock %}
```

```html
<!-- studyhub/templates/_review_card.html -->
{% if card %}
  <p class="muted">{{ remaining }} more due in this deck</p>

  <article class="flashcard">
    <div class="face front">{{ card.front }}</div>
    <details class="face back">
      <summary>Show answer</summary>
      <p>{{ card.back }}</p>
    </details>
  </article>

  <form class="grades"
        hx-post="/review/{{ card.id }}/answer"
        hx-target="#review-pane"
        hx-swap="innerHTML">
    <input type="hidden" name="deck_id" value="{{ deck_id }}">
    <button type="submit" class="again" name="rating" value="1">
      Again <small>{{ preview.again }}</small>
    </button>
    <button type="submit" class="hard" name="rating" value="2">
      Hard <small>{{ preview.hard }}</small>
    </button>
    <button type="submit" class="good" name="rating" value="3">
      Good <small>{{ preview.good }}</small>
    </button>
    <button type="submit" class="easy" name="rating" value="4">
      Easy <small>{{ preview.easy }}</small>
    </button>
  </form>
{% else %}
  <p class="done">Nothing due right now. Nice.</p>
  <a class="btn" href="/decks">Back to decks</a>
{% endif %}
```

Three details worth understanding:

1. `hx-target="#review-pane"` + `hx-swap="innerHTML"` — the response is a fragment, not a page.
   The browser never navigates; the pane is replaced in place.
2. The submit button's `name="rating" value="3"` is included in the POST body. HTMX serialises
   the form *and* the submitting button, so you get one endpoint and four behaviours. That is why
   `grade_card_html` takes `rating: int = Form(ge=1, le=4)`.
3. The partial is included by `review.html` on first render *and* returned by the endpoint. Same
   template, two callers. That is the whole HTMX pattern: fragments are just templates that
   happen to be renderable on their own.

```html
<!-- studyhub/templates/decks.html (body only) -->
{% extends "base.html" %}
{% block content %}
<header class="page-header">
  <h1>Your decks</h1>
  <a class="btn" href="/browse">Browse public decks</a>
</header>

<ul class="deck-grid">
  {% for deck, card_count in decks %}
    <li class="deck-card">
      <a href="/decks/{{ deck.id }}"><h2>{{ deck.title }}</h2></a>
      <p class="muted">{{ card_count }} cards · {% if deck.is_public %}public{% else %}private{% endif %}</p>
      <div class="row">
        <a class="btn" href="/decks/{{ deck.id }}/review">Study</a>
        <form method="post" action="/decks/{{ deck.id }}/export?format=json">
          <button class="link">Export JSON</button>
        </form>
      </div>
    </li>
  {% else %}
    <li class="empty">No decks yet. Create one below.</li>
  {% endfor %}
</ul>

<form class="new-deck" method="post" action="/decks">
  <input name="title" placeholder="Deck title" required maxlength="200">
  <input name="description" placeholder="Description (optional)">
  <button type="submit">Create deck</button>
</form>
{% endblock %}
```

Login page (the form posts to the page route, which redirects):

```html
<!-- studyhub/templates/login.html -->
{% extends "base.html" %}
{% block content %}
<h1>Log in</h1>

{% if error %}<p class="flash error">{{ error }}</p>{% endif %}

<form class="stack" method="post" action="/login">
  <label>Email <input type="email" name="email" required autofocus></label>
  <label>Password <input type="password" name="password" required></label>
  <button type="submit">Log in</button>
</form>
<p class="muted">No account? <a href="/register">Register</a>.</p>
{% endblock %}
```

`register.html` is the same shape with a third field:

```html
<!-- studyhub/templates/register.html -->
{% extends "base.html" %}
{% block content %}
<h1>Create your account</h1>

{% if error %}<p class="flash error">{{ error }}</p>{% endif %}

<form class="stack" method="post" action="/register">
  <label>Email <input type="email" name="email" required autofocus></label>
  <label>Display name <input name="display_name" required maxlength="80"></label>
  <label>Password <input type="password" name="password" required minlength="8"></label>
  <button type="submit">Sign up</button>
</form>
<p class="muted">Already registered? <a href="/login">Log in</a>.</p>
{% endblock %}
```

## Milestone 5: stats & the dashboard

The aggregation is one `GROUP BY`, but the interesting part is what happens *after* the query:
days with no reviews must still appear as zero-height bars, and the streak has to be computed in
the user's timezone, not the server's.

```python
# studyhub/services.py — append StatsService (add `func`, `select` to the sqlalchemy import)
from datetime import date, timedelta

from studyhub.models import Card, Deck, ReviewLog, User
from studyhub.repositories import ReviewLogRepository
from studyhub.schemas import DailyPoint, StatsSummary

WINDOW_DAYS = 30


class StatsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.logs = ReviewLogRepository(session)

    def daily(self, user: User) -> list[DailyPoint]:
        now = timeutils.utcnow()
        today = timeutils.local_day(now, user.timezone)
        window = timeutils.last_n_days(today, WINDOW_DAYS)
        counts = {day: (reviews, remembered) for day, reviews, remembered in self.logs.daily_counts(user.id, window[0])}
        return [
            DailyPoint(
                day=day,
                reviews=counts.get(day, (0, 0))[0],
                remembered=counts.get(day, (0, 0))[1],
            )
            for day in window
        ]

    def summary(self, user: User) -> StatsSummary:
        now = timeutils.utcnow()
        today = timeutils.local_day(now, user.timezone)
        end_of_today = timeutils.end_of_local_day(now, user.timezone)

        total_cards = int(
            self.session.scalar(
                select(func.count(Card.id)).join(Deck).where(Deck.owner_id == user.id)
            )
            or 0
        )
        due_today = int(
            self.session.scalar(
                select(func.count(Card.id))
                .join(Deck)
                .where(Deck.owner_id == user.id, Card.due_at <= end_of_today)
            )
            or 0
        )
        new_cards = int(
            self.session.scalar(
                select(func.count(Card.id))
                .join(Deck)
                .where(Deck.owner_id == user.id, Card.state == "new")
            )
            or 0
        )
        reviews_today = int(
            self.session.scalar(
                select(func.count(ReviewLog.id)).where(
                    ReviewLog.user_id == user.id, ReviewLog.local_day == today
                )
            )
            or 0
        )

        points = self.daily(user)
        graded = sum(point.reviews for point in points)
        remembered = sum(point.remembered for point in points)
        retention = round(remembered / graded * 100, 1) if graded else 0.0
        streak = self._streak(self.logs.distinct_days(user.id), today)

        return StatsSummary(
            due_today=due_today,
            reviews_today=reviews_today,
            new_cards=new_cards,
            total_cards=total_cards,
            retention_30d=retention,
            streak_days=streak,
        )

    @staticmethod
    def _streak(days: set[str], today: str) -> int:
        if not days:
            return 0
        cursor = date.fromisoformat(today)
        if today not in days:
            cursor -= timedelta(days=1)
            if cursor.isoformat() not in days:
                return 0
        streak = 0
        while cursor.isoformat() in days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak
```

Filling the gaps in Python rather than in SQL is the right trade here: 30 iterations of a dict
lookup is free, and a SQL solution (generate_series on Postgres, a recursive CTE on SQLite) is
dialect-specific and harder to read. Do not be clever about 30 rows.

```html
<!-- studyhub/templates/stats.html (body only) -->
{% extends "base.html" %}
{% block content %}
<h1>Your stats</h1>

<ul class="kpis">
  <li><strong>{{ stats.due_today }}</strong><span>due today</span></li>
  <li><strong>{{ stats.reviews_today }}</strong><span>reviews today</span></li>
  <li><strong>{{ "%.0f"|format(stats.retention_30d) }}%</strong><span>retention (30d)</span></li>
  <li><strong>{{ stats.streak_days }}</strong><span>day streak</span></li>
  <li><strong>{{ stats.total_cards }}</strong><span>cards</span></li>
</ul>

{% set peak = daily | map(attribute="reviews") | max or 1 %}
<ul class="chart" role="img" aria-label="Reviews per day, last 30 days">
  {% for point in daily %}
    <li title="{{ point.day }}: {{ point.reviews }} reviews">
      <div class="bar" style="height: {{ (point.reviews / peak * 100) | round | int }}%"></div>
    </li>
  {% endfor %}
</ul>
<div class="chart-axis"><span>{{ daily[0].day }}</span><span>{{ daily[-1].day }}</span></div>
{% endblock %}
```

```css
/* studyhub/static/app.css (chart section) */
.chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 180px;
  margin: 0;
  padding: 8px;
  list-style: none;
  background: #0f172a;
  border-radius: 10px;
}
.chart li { flex: 1 1 0; display: flex; align-items: flex-end; height: 100%; }
.chart .bar {
  width: 100%;
  min-height: 2px;
  background: linear-gradient(#38bdf8, #0284c7);
  border-radius: 2px 2px 0 0;
}
.chart-axis { display: flex; justify-content: space-between; font-size: 0.8rem; opacity: 0.6; }
.kpis { display: flex; gap: 12px; list-style: none; padding: 0; flex-wrap: wrap; }
.kpis li {
  flex: 1 1 120px;
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 10px;
  padding: 12px;
  text-align: center;
}
.kpis strong { display: block; font-size: 1.8rem; }
```

No charting library. `flex` with `align-items: flex-end` plus a percentage height is a bar chart.
It loads instantly, works with JavaScript disabled, and there is no dependency to keep updated.
Reach for a JS chart library when you need tooltips, zoom, or live updates — not before.

:::scenario A user reports "my streak reset overnight and I definitely studied yesterday"
Support ticket, 8am. The user is in Sydney (UTC+11). They did reviews at 9pm local time. Your
server is UTC. The dashboard says streak = 0.
:::

:::solution You bucketed by server day instead of user day
The bug: `ReviewLog.reviewed_at` is stored in UTC, and the streak grouped by that timestamp's
date. 9pm in Sydney is 10am UTC *the same day* — fine — but a 1am Sydney review is 2pm UTC the
*previous* day, so it lands in yesterday's bucket, and anyone who studies late sees their streak
break at midnight UTC, which is 11am their time.

Fix it at write time, not read time. Add a `local_day` column, populate it when the review is
recorded using the user's own timezone, and group by it:

```python
local_day=timeutils.local_day(now, user.timezone)
```

Then every downstream computation — streak, "reviews today", the 30-day chart — keys off
`local_day` and is automatically correct per user. Backfill existing rows with one Alembic data
migration:

```sql
UPDATE review_logs SET local_day = '1970-01-01' WHERE local_day IS NULL;
```

then recompute properly in Python, or accept that historic streaks are approximate. Also make
timezone editable in the user's profile — a hardcoded `UTC` default is a lie for most of the
planet. This is why `User.timezone` exists in the model from day one.
:::

## Milestone 6: tests

The fixture stack does three things: force test settings before the app imports, use an in-memory
SQLite database with a single shared connection, and override the session dependency so every
request joins the test's transaction.

```python
# tests/conftest.py
from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

os.environ["STUDYHUB_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["STUDYHUB_SECRET_KEY"] = "test-secret-key"
os.environ["STUDYHUB_COOKIE_SECURE"] = "false"

from studyhub.db import get_session          # noqa: E402  (import after env vars)
from studyhub.main import app                # noqa: E402
from studyhub.models import Base, Card, ReviewLog, User  # noqa: E402
from studyhub.timeutils import utcnow        # noqa: E402


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield db
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_client(client) -> TestClient:
    response = client.post(
        "/api/auth/register",
        json={"email": "ada@example.com", "display_name": "Ada", "password": "correct-horse"},
    )
    assert response.status_code == 201, response.text
    return client
```

The transaction-per-test pattern means tests never clean up and never leak into each other:
`transaction.rollback()` at the end undoes everything. `join_transaction_mode="create_savepoint"`
lets the session `commit()` inside service code without ending the outer test transaction.

Scheduler tests are in Milestone 1. Service tests exercise the rules directly:

```python
# tests/test_services.py
import pytest
from sqlalchemy import func, select

from studyhub.models import Card, Deck, ReviewLog, User
from studyhub.services import AuthService, DeckService, ReviewService, StatsService
from studyhub.errors import DuplicateEmailError, ForbiddenError, NotFoundError


def test_password_is_hashed(session):
    user = AuthService(session).register("a@b.com", "Ada", "hunter2000")
    assert user.password_hash != "hunter2000"
    assert user.password_hash.startswith("$2b$")


def test_duplicate_email_rejected(session):
    service = AuthService(session)
    service.register("a@b.com", "Ada", "hunter2000")
    with pytest.raises(DuplicateEmailError):
        service.register("a@b.com", "Other", "hunter2000")
    session.rollback()


def test_cannot_touch_another_users_deck(session):
    owner = AuthService(session).register("owner@example.com", "Owner", "password123")
    stranger = AuthService(session).register("stranger@example.com", "Stranger", "password123")
    deck = DeckService(session).create(owner, "Private")
    with pytest.raises(ForbiddenError):
        DeckService(session).require_owned(deck.id, stranger.id)


def test_grading_writes_state_and_log(session):
    user = AuthService(session).register("rev@example.com", "Rev", "password123")
    deck = DeckService(session).create(user, "Spanish")
    card = DeckService(session).add_card(deck.id, user.id, "hablar", "to speak")

    updated, outcome = ReviewService(session).grade(user, card.id, 3, duration_ms=1500)

    assert outcome.interval_days == 1.0
    assert updated.repetitions == 1
    assert updated.due_at > utcnow()
    log = session.scalar(select(ReviewLog).where(ReviewLog.card_id == card.id))
    assert log.rating == 3
    assert log.interval_before == 0.0
    assert log.interval_after == 1.0
    assert log.duration_ms == 1500


def test_clone_copies_cards_but_not_ownership(session):
    author = AuthService(session).register("author@example.com", "Author", "password123")
    reader = AuthService(session).register("reader@example.com", "Reader", "password123")
    decks = DeckService(session)
    original = decks.create(author, "Capitals", is_public=True)
    decks.add_card(original.id, author.id, "France", "Paris")
    decks.add_card(original.id, author.id, "Peru", "Lima")

    copy = decks.clone_public(original.id, reader)

    assert copy.owner_id == reader.id
    assert copy.is_public is False
    assert len(copy.cards) == 2
    assert copy.title.endswith("(copy)")


def test_clone_rejects_private_deck(session):
    author = AuthService(session).register("a2@example.com", "A", "password123")
    voyeur = AuthService(session).register("v@example.com", "V", "password123")
    private = DeckService(session).create(author, "Secret")
    with pytest.raises(NotFoundError):
        DeckService(session).clone_public(private.id, voyeur)


def test_stats_summary_counts_due_and_streak(session):
    user = AuthService(session).register("stats@example.com", "Stats", "password123")
    decks = DeckService(session)
    deck = decks.create(user, "Geography")
    card = decks.add_card(deck.id, user.id, "Peru", "Lima")
    ReviewService(session).grade(user, card.id, 3)

    summary = StatsService(session).summary(user)

    assert summary.total_cards == 1
    assert summary.reviews_today == 1
    assert summary.streak_days == 1
    assert summary.retention_30d == 100.0
```

End-to-end HTTP tests, including the HTMX fragment:

```python
# tests/test_review_flow.py
from datetime import timedelta

from sqlalchemy import func, select

from studyhub.models import Card, ReviewLog
from studyhub.timeutils import utcnow


def test_full_review_flow_over_http(user_client, session):
    deck_id = user_client.post("/api/decks", json={"title": "Spanish"}).json()["id"]
    card_id = user_client.post(
        f"/api/decks/{deck_id}/cards", json={"front": "hablar", "back": "to speak"}
    ).json()["id"]

    queue = user_client.get("/api/review/queue").json()
    assert [card["id"] for card in queue] == [card_id]

    response = user_client.post(f"/api/review/{card_id}", json={"rating": 3, "duration_ms": 900})
    assert response.status_code == 200
    body = response.json()
    assert body["interval_days"] == 1.0
    assert body["ease_factor"] == 2.5
    assert body["remaining_due"] == 0

    card = session.get(Card, card_id)
    assert card.repetitions == 1
    assert card.due_at > utcnow()
    assert session.scalar(select(func.count()).select_from(ReviewLog)) == 1

    assert user_client.get("/api/review/queue").json() == []


def test_htmx_answer_returns_fragment(user_client):
    deck_id = user_client.post("/api/decks", json={"title": "Verbs"}).json()["id"]
    first = user_client.post(
        f"/api/decks/{deck_id}/cards", json={"front": "ser", "back": "to be"}
    ).json()["id"]
    user_client.post(f"/api/decks/{deck_id}/cards", json={"front": "ir", "back": "to go"})

    response = user_client.post(
        f"/review/{first}/answer", data={"deck_id": deck_id, "rating": 3}
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "to go" in response.text        # the next card is swapped in
    assert "Again" in response.text        # and it carries the four grade buttons


def test_again_puts_the_card_back_in_ten_minutes(user_client, session):
    deck_id = user_client.post("/api/decks", json={"title": "Verbs"}).json()["id"]
    card_id = user_client.post(
        f"/api/decks/{deck_id}/cards", json={"front": "ser", "back": "to be"}
    ).json()["id"]

    user_client.post(f"/review/{card_id}/answer", data={"deck_id": deck_id, "rating": 1})

    card = session.get(Card, card_id)
    assert card.repetitions == 0
    assert card.lapses == 1
    assert card.due_at < utcnow() + timedelta(minutes=11)


def test_review_requires_authentication(client):
    assert client.get("/api/review/queue").status_code == 401


def test_pages_redirect_to_login_when_anonymous(client):
    response = client.get("/decks", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/login"
```

```python
# tests/test_auth_api.py
from studyhub.models import User


def test_register_sets_cookie(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "new@example.com", "display_name": "New", "password": "password123"},
    )
    assert response.status_code == 201
    assert "studyhub_session" in response.cookies


def test_short_password_rejected(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "x@example.com", "display_name": "X", "password": "short"},
    )
    assert response.status_code == 422


def test_me_returns_current_user(user_client):
    assert user_client.get("/api/auth/me").json()["email"] == "ada@example.com"


def test_logout_clears_cookie(user_client):
    user_client.post("/api/auth/logout")
    assert user_client.get("/api/auth/me").status_code == 401
```

```bash
python3 -m pytest -q
```

```text
38 passed in 1.42s
```

:::pitfall Forgetting to set env vars before importing the app
`os.environ[...] = ...` in `conftest.py` is pointless if `studyhub.main` was imported at the top
of the file — the settings object is already built. Import the app *after* setting the variables
(the `noqa: E402` imports above), or set them in `[tool.pytest.ini_options] env = [...]` with
`pytest-env`. Symptom: tests pass locally and fail in CI because CI has a real `.env`.
:::

## Milestone 7: ship it

```toml
# pyproject.toml
[project]
name = "studyhub"
version = "1.0.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115",
  "uvicorn[standard]>=0.30",
  "sqlalchemy>=2.0",
  "alembic>=1.13",
  "pydantic>=2.7",
  "pydantic-settings>=2.3",
  "pydantic[email]>=2.7",
  "jinja2>=3.1",
  "python-multipart>=0.0.9",
  "passlib[bcrypt]>=1.7.4",
  "itsdangerous>=2.2",
  "psycopg[binary]>=3.2",
]

[project.optional-dependencies]
dev = ["pytest>=8.2", "httpx>=0.27", "ruff>=0.6"]

[tool.pytest.ini_options]
addopts = "-q"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

```dockerfile
# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install . && pip install "psycopg[binary]"

COPY alembic.ini ./
COPY alembic ./alembic
COPY studyhub ./studyhub

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn studyhub.main:app --host 0.0.0.0 --port 8000"]
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: studyhub
      POSTGRES_PASSWORD: studyhub
      POSTGRES_DB: studyhub
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U studyhub"]
      interval: 5s
      timeout: 3s
      retries: 10

  web:
    build: .
    depends_on:
      db:
        condition: service_healthy
    environment:
      STUDYHUB_DATABASE_URL: postgresql+psycopg://studyhub:studyhub@db:5432/studyhub
      STUDYHUB_SECRET_KEY: ${STUDYHUB_SECRET_KEY:?set it in .env}
      STUDYHUB_COOKIE_SECURE: "true"
    ports:
      - "8000:8000"

volumes:
  pgdata:
```

```yaml
# .github/workflows/ci.yml
name: ci
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -e ".[dev]"
      - run: ruff check .
      - run: pytest
  image:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t studyhub:${{ github.sha }} .
```

Migrations run in the container's `CMD`, before uvicorn starts. Two rules: never run `upgrade
head` from more than one replica at once (use a migration job in your orchestrator if you scale
out), and always take a database snapshot before a deploy that contains a destructive migration.

Pre-launch checklist:

- `STUDYHUB_SECRET_KEY` is a real random value, not the default. (`python3 -c "import secrets; print(secrets.token_urlsafe(48))"`)
- `STUDYHUB_COOKIE_SECURE=true` and the app is only reachable over HTTPS.
- `STUDYHUB_DATABASE_URL` points at Postgres, not the SQLite default.
- `alembic upgrade head` succeeds against a clean database *and* against a copy of production.
- `alembic downgrade -1` also succeeds — you have tested the rollback you are relying on.
- Backups exist and you have restored from one at least once.
- `pytest` passes in CI, not just on your machine.
- A 500 renders a page, not a stack trace (`DEBUG` off, no `Server header` leaking versions).
- Passwords are hashed, cookies are `HttpOnly` + `SameSite=Lax`, and no secret is in the image.
- Logs go to stdout and include a request id.
- `/healthz` exists and returns 200 without touching the database.

:::scenario The review endpoint gets slow once a user has 50,000 cards
It was fine with 500. Now `POST /api/review/{card_id}` takes two seconds and the dashboard takes
five. You open the logs and see full table scans on `cards`.
:::

:::solution Index the columns you filter and sort on, and stop fetching what you do not need
Two separate problems hide behind "it's slow".

**1. Missing composite index.** `due_cards` filters on `Deck.owner_id` and `Card.due_at <= now`
and sorts by `due_at`. With a single-column index on `due_at` (or none), Postgres scans and
sorts. The composite index already in the migration fixes it:

```sql
CREATE INDEX ix_cards_deck_due ON cards (deck_id, due_at);
CREATE INDEX ix_decks_owner_id ON decks (owner_id);
```

Verify rather than assume:

```sql
EXPLAIN ANALYZE
SELECT c.* FROM cards c JOIN decks d ON c.deck_id = d.id
WHERE d.owner_id = 42 AND c.due_at <= now()
ORDER BY c.due_at LIMIT 20;
```

You want to see `Index Scan using ix_cards_deck_due` and `Limit`, not `Seq Scan on cards` plus
`Sort`. If the planner still chooses a scan, run `ANALYZE cards;` — stale statistics are the
usual reason a correct index is ignored.

**2. The N+1 in the dashboard.** `DeckService.list_for` counts cards with a correlated
subquery, which is fine, but `len(copy.cards)` in `clone_public`'s caller and any
`deck.cards` access in a loop triggers one SELECT per deck. Either keep the scalar-subquery
count (preferred — one query total) or add `lazy="selectin"` to the relationship so SQLAlchemy
loads all collections in one extra round trip. Twenty decks is 20 queries versus 1; at 200 decks
the page stops loading.

Then measure again with a realistic seed — write a script that inserts 50k cards before you
start optimising, because you cannot fix what you cannot reproduce.
:::

## Where to take it next

Each of these is a real feature, not a stretch goal. Pick one and ship it.

1. **Scheduler tuning.** Add a learning-steps ladder (1m → 10m → 1d) for new cards instead of
   jumping straight to a day, and add a "fuzz" of ±5% to intervals so cards reviewed together
   do not all come due on the same day forever.
2. **Mobile PWA.** A `manifest.webmanifest`, an icon, and a service worker that caches the shell.
   The review screen works offline if you queue grades and replay them on reconnect.
3. **Images and audio on cards.** A uploads table, a `Card.front_image_id`, and an
   `/uploads/{id}` route serving from local disk now, S3 later. Remember to validate content type
   and cap the size.
4. **Collaborative decks.** A `deck_members` association table with a role column
   (`viewer` / `editor`), so a study group shares one deck. This is where you add permission
   checks to every deck-related service method — do it once, in the service.
5. **A public JSON API for a mobile client.** You already have `/api/*`. Add API-key auth
   (a `tokens` table plus a `X-API-Key` dependency), pagination with cursor tokens, and
   `/api/openapi.json` documentation that a mobile team could build against.
6. **Rate limiting.** `slowapi` or a Redis token bucket on `/api/auth/login` and
   `/api/auth/register`. Five attempts per minute per IP kills credential stuffing.
7. **Admin panel.** A `/admin` router behind an `is_admin` flag: user list, deck list, disable
   account, delete abusive public deck. Write an `admin_required` dependency that composes
   `current_user` and checks the flag.
8. **Heatmap instead of a bar chart.** Same aggregation query, 365 days, CSS grid of cells
   coloured by bucket. This is the single highest-impact UI change in the app.
9. **Scheduler A/B testing.** Store `scheduler_version` on the review log, run two algorithms
   behind a feature flag, compare retention at 30 days. This is why the logs are append-only.
10. **Undo.** A `undo_last_review` endpoint that reads the most recent log row and restores the
    `*_before` values onto the card, then deletes that log row. Ten lines, and it is the feature
    users ask for first.

## Key takeaways

- A pure core (no DB, no clock, no framework) makes the hard logic testable in milliseconds and
  reusable anywhere; everything else is plumbing around it.
- Repositories own SQL, services own rules and transactions, routers own HTTP — one file per
  question when you debug.
- Store computed scheduling state on the card so "what is due" is an indexed query, and keep an
  append-only log so history and analytics survive schema and algorithm changes.
- Store naive UTC everywhere, and derive the user's calendar day into a `local_day` column at
  write time so streaks and daily stats are correct per user.
- `response_model` on every route is what keeps `password_hash` and internal columns out of your
  API responses.
- Dependencies compose: `current_user` raises JSON 401, `current_user_page` wraps it and raises a
  307 to `/login`.
- HTMX means fragments are just templates — render `_review_card.html` both from the page and
  from the endpoint, and let the submitting button's `name`/`value` carry the grade.
- Tests use one transaction per test with `join_transaction_mode="create_savepoint"` and a
  `dependency_overrides` swap for `get_session`, so service `commit()` calls still roll back.
- Run `alembic upgrade head` in the container's `CMD` before uvicorn, and test `downgrade` too.
- A bar chart is `display: flex; align-items: flex-end` plus a percentage height. No JS library
  required.

## Milestone checklist

- [ ] Milestone 1 — `scheduler.py` written test-first; 14 scheduler tests green in under a second.
- [ ] Milestone 2 — models, repositories, services, and the initial Alembic migration applied.
- [ ] Milestone 3 — auth, decks, cards, review, stats, and import/export routers mounted; 401 and
      403 verified by hand and by test.
- [ ] Milestone 4 — base template, deck list, deck detail, login, and the HTMX review screen
      swapping without a full reload.
- [ ] Milestone 5 — stats aggregation and the CSS bar chart rendering 30 days including zero days.
- [ ] Milestone 6 — 38+ tests passing: scheduler, services, auth API, full review flow end to end.
- [ ] Milestone 7 — Docker build, `docker compose up`, CI green, pre-launch checklist ticked.
- [ ] Stretch — pick one extension from "Where to take it next" and merge it.

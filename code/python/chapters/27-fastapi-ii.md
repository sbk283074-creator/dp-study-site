---
chapter: 27
part: 4
title: "FastAPI II: Database, Auth & Testing"
summary: Wire SQLAlchemy 2.x into FastAPI, split schemas from ORM models, build full CRUD with ownership rules, and add password hashing, cookie sessions, authorization and a test suite that runs against a fresh database.
minutes: 60
tags: [sqlalchemy, fastapi, authentication, jwt, authorization, pytest, pydantic-settings]
---

Chapter 26 served data from a dictionary. That is fine for learning routing and useless for
anything real: a restart loses everything, two users see each other's data, and passwords have
nowhere to live. This chapter replaces the dictionary with SQLAlchemy 2.x, adds users, and answers
the two questions every application eventually faces — who are you, and are you allowed to touch
this record? By the end you have the API half of StudyHub, the capstone you start in Chapter 30,
and a test suite fast enough to run on every save.

## Installing the stack

```bash
python3 -m pip install "sqlalchemy>=2" "pydantic-settings" "passlib[bcrypt]" \
  "python-jose[cryptography]" "python-multipart" "email-validator" alembic pytest
```

`python-multipart` is required for HTML form posts; `email-validator` backs Pydantic's `EmailStr`;
`alembic` handles migrations from Chapter 29 onward.

## Wiring SQLAlchemy 2.x into FastAPI

You met SQLAlchemy in Chapter 19. The web-specific concern is **session scope**: a session must
live for exactly one request, then close. FastAPI's dependency system with `yield` gives you that
directly.

```python
# app/database.py
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.settings import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

Three choices worth understanding:

- `pool_pre_ping=True` — connection pools go stale when a database restarts or a firewall drops
  idle connections. The pre-ping costs one cheap round trip and removes a class of 3am 500s.
- `expire_on_commit=False` — by default SQLAlchemy expires every attribute after a commit, so
  reading `deck.name` afterwards issues a fresh `SELECT`. In a request handler that refresh
  happens while Pydantic is building your response, and it can fail after the session closes.
  Turning expiry off keeps the instance usable.
- `yield` in the dependency — the code after `yield` runs when the response is finished, so the
  `with` block closes the session even if the handler raised. Never `return` here.

Create tables once at startup:

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import auth, cards, decks


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="StudyHub", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(decks.router)
app.include_router(cards.router)
```

`lifespan` is the modern replacement for the deprecated `@app.on_event("startup")`. `create_all`
is acceptable while the schema is young; Chapter 29 replaces it with Alembic so schema changes
are versioned and reversible.

## ORM models and the schema split

The most important structural decision in a FastAPI project: **storage models and wire models are
different things.** One file each.

```python
# app/models.py
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    decks: Mapped[List["Deck"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(280), default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    owner: Mapped[User] = relationship(back_populates="decks")
    cards: Mapped[List["Card"]] = relationship(
        back_populates="deck", cascade="all, delete-orphan"
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    front: Mapped[str] = mapped_column(String(200))
    back: Mapped[str] = mapped_column(String(500))
    deck_id: Mapped[int] = mapped_column(ForeignKey("decks.id"), index=True)

    deck: Mapped["Deck"] = relationship(back_populates="cards")
```

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool


class DeckCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=280)


class DeckUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=280)


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    front: str
    back: str


class DeckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    owner_id: int


class DeckReadWithCards(DeckRead):
    cards: list[CardRead] = []
```

`model_config = ConfigDict(from_attributes=True)` lets Pydantic read attributes off an ORM object
instead of dict keys. Note what `UserRead` does **not** contain: `hashed_password`. It cannot
leak, because the field does not exist on the response type.

## Full CRUD for one resource

```python
# app/routers/decks.py
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.deps import CurrentUser, SessionDep
from app.models import Card, Deck
from app.schemas import DeckCreate, DeckRead, DeckReadWithCards, DeckUpdate

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=list[DeckRead])
def list_decks(
    session: SessionDep,
    current_user: CurrentUser,
    q: Annotated[str | None, Query(max_length=50)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Deck]:
    stmt = select(Deck).where(Deck.owner_id == current_user.id)
    if q:
        stmt = stmt.where(Deck.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Deck.id.desc()).offset(offset).limit(limit)
    return list(session.scalars(stmt).all())


@router.post("/", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(payload: DeckCreate, session: SessionDep, current_user: CurrentUser) -> Deck:
    deck = Deck(**payload.model_dump(), owner_id=current_user.id)
    session.add(deck)
    session.commit()
    session.refresh(deck)
    return deck


@router.patch("/{deck_id}", response_model=DeckRead)
def update_deck(
    deck_id: int, payload: DeckUpdate, session: SessionDep, current_user: CurrentUser
) -> Deck:
    deck = session.get(Deck, deck_id)
    if deck is None or deck.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(deck, field, value)
    session.commit()
    return deck


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(deck_id: int, session: SessionDep, current_user: CurrentUser) -> None:
    deck = session.get(Deck, deck_id)
    if deck is None or deck.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    session.delete(deck)
    session.commit()
```

`session.scalars(stmt).all()` is the SQLAlchemy 2.x form; `session.query(...)` is legacy. The
ownership filter lives in the query itself (`where(Deck.owner_id == current_user.id)`) rather
than in a check after fetching — you never load a row the caller is not allowed to see.

## Relationships: `selectinload`

Returning a deck with its cards naively triggers one query per deck:

```python
stmt = select(Deck).where(Deck.id == deck_id)
deck = session.scalars(stmt).one()
print(len(deck.cards))     # a second SELECT, here
```

FastAPI serializes the response after the handler returns, so that second `SELECT` happens in the
middle of building JSON — fine locally, an N+1 disaster with fifty rows. Load it up front:

```python
from sqlalchemy.orm import selectinload


@router.get("/{deck_id}", response_model=DeckReadWithCards)
def get_deck(deck_id: int, session: SessionDep, current_user: CurrentUser) -> Deck:
    stmt = (
        select(Deck)
        .options(selectinload(Deck.cards))
        .where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    )
    deck = session.scalars(stmt).one_or_none()
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck
```

`selectinload` issues one extra `SELECT ... WHERE deck_id IN (...)` for the whole collection. Use
`joinedload` when you are fetching a single parent and want one round trip; use `selectinload` for
collections. Chapter 37 revisits N+1 with a profiler.

## Password hashing

Never store a password. Store a hash from a slow, salted algorithm.

```python
# app/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
```

```python
>>> h = hash_password("correct horse battery")
>>> h
'$2b$12$K1xQ...'
>>> verify_password("correct horse battery", h)
True
>>> verify_password("wrong", h)
False
```

:::note `passlib` is on life support
`passlib` still works but is barely maintained and logs a warning with bcrypt 4.x. The modern
alternative is `pwdlib` (`pip install pwdlib[bcrypt]`), with `PasswordHash.recommended()` giving
you `hash()` and `verify()`. The interface is nearly identical; only the import changes.
:::

## Tokens: JWT vs cookies

A **JWT** is a signed string the client sends back on every request, so the server keeps no
session state — good for mobile clients and separate front-ends. A **cookie session** is a
random ID pointing at a row in your database; it can be revoked instantly, but it needs storage
and a lookup per request.

For a server-rendered app (Chapter 28 is exactly that), put the JWT in an `HttpOnly` cookie: the
browser sends it automatically, JavaScript cannot read it, and you still get statelessness.

```python
# app/security.py (continued)
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.settings import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def create_access_token(subject: int, expires_minutes: int = 60 * 24) -> str:
    payload = {
        "sub": str(subject),
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
```

Passing `algorithms=[ALGORITHM]` explicitly is not optional style — omitting it is how the
"alg: none" bypass happens.

```python
# app/routers/auth.py
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import select

from app.database import SessionDep
from app.models import User
from app.schemas import UserCreate, UserRead
from app.security import create_access_token, decode_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, session: SessionDep) -> User:
    exists = session.scalar(select(User).where(User.email == payload.email))
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=UserRead)
def login(payload: LoginRequest, response: Response, session: SessionDep) -> User:
    user = session.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )
    response.set_cookie(
        key="access_token",
        value=create_access_token(user.id),
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=60 * 60 * 24,
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie("access_token")
```

The failure message is identical for "no such email" and "wrong password". Telling the user which
one happened turns your login form into an account-enumeration tool.

## `get_current_user` and authorization

```python
# app/deps.py
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionDep
from app.models import User
from app.security import decode_access_token


def get_current_user(
    session: SessionDep,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = None if access_token is None else decode_access_token(access_token)
    if user_id is None:
        raise unauthorized
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
```

Any endpoint that takes `current_user: CurrentUser` is now authenticated, and the dependency
appears in `/docs` as a lock icon. For authorization, load the resource **and** check ownership
in one step:

```python
# app/deps.py (continued)
from fastapi import Path
from app.models import Deck


def get_owned_deck(
    deck_id: Annotated[int, Path(ge=1)],
    session: SessionDep,
    current_user: CurrentUser,
) -> Deck:
    deck = session.scalars(
        select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    ).one_or_none()
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck


OwnedDeck = Annotated[Deck, Depends(get_owned_deck)]
```

:::pitfall 403 where 404 is correct
Returning `403 Forbidden` for someone else's deck confirms that deck `412` exists. An attacker
enumerating `/decks/{id}` then knows exactly which IDs are real and can probe further. Use 404
for both "does not exist" and "not yours" — the caller learns nothing. Reserve 403 for
authenticated users hitting a genuinely forbidden action, such as a non-admin calling an admin
route.
:::

## Settings with `pydantic-settings`

Configuration belongs in the environment, not in source. `pydantic-settings` reads environment
variables and a `.env` file into a typed object, failing at startup if something is missing.

```python
# app/settings.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "StudyHub"
    debug: bool = False
    database_url: str = "sqlite:///./studyhub.db"
    secret_key: str = "dev-only-change-me"
    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

```bash
# .env  — never commit this file
DATABASE_URL=postgresql+psycopg://studyhub:studyhub@localhost:5432/studyhub
SECRET_KEY=9f2c...long-random-string...
CORS_ORIGINS=["http://localhost:8000"]
```

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Add `.env` to `.gitignore` on day one. In production these values come from your host's secret
store, not from a file (Chapter 29).

## CORS

A browser refuses to let JavaScript on `app.example.com` read a response from `api.example.com`
unless the server says it is allowed:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

With `allow_credentials=True` you cannot use `"*"` for origins — browsers reject it, and rightly
so. CORS is a browser rule only; `curl` and your tests ignore it completely, which is why CORS
bugs always show up in someone else's browser.

## Middleware: request timing

```python
import logging
import time

from fastapi import Request

logger = logging.getLogger("studyhub.access")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{duration_ms:.1f}ms"
    logger.info("%s %s -> %s in %.1fms",
                request.method, request.url.path, response.status_code, duration_ms)
    return response
```

`@app.middleware("http")` is the convenient form. For anything perf-sensitive, write a pure ASGI
middleware class instead; it avoids the thread-pool hop that `BaseHTTPMiddleware` performs.

## Background tasks

Anything slow that the response does not depend on — welcome emails, thumbnails, webhooks — goes
into a background task:

```python
from fastapi import BackgroundTasks


def send_welcome_email(email: str) -> None:
    logger.info("sending welcome email to %s", email)


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, background_tasks: BackgroundTasks, session: SessionDep) -> User:
    ...
    background_tasks.add_task(send_welcome_email, user.email)
    return user
```

Tasks run after the response is sent, inside your app process. That is fine for a two-second
email and wrong for a five-minute report — that belongs in a real queue like Celery or RQ.

## Pagination and filtering in the query layer

Return a total count so the client can render page numbers:

```python
def search_decks(session: Session, *, owner_id: int, q: str | None = None,
                 limit: int = 20, offset: int = 0) -> tuple[list[Deck], int]:
    stmt = select(Deck).where(Deck.owner_id == owner_id)
    if q:
        stmt = stmt.where(Deck.name.ilike(f"%{q}%"))
    total = session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = list(session.scalars(stmt.order_by(Deck.id.desc()).offset(offset).limit(limit)))
    return items, total
```

Keeping this in a function rather than inline in the router means you can unit-test query
behaviour directly. Escape `%` and `_` in user input before `ilike`, or a search for `100%` matches
everything.

## Testing

The pattern that makes API tests trustworthy: **a fresh database per test** and
**`dependency_overrides` to fake authentication**.

```python
# tests/conftest.py
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_session
from app.main import app
from app.models import Base, User
from app.security import hash_password


@pytest.fixture()
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(session: Session) -> Iterator[TestClient]:
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def user(session: Session) -> User:
    u = User(email="ada@example.com", hashed_password=hash_password("hunter2hunter2"))
    session.add(u)
    session.commit()
    return u


@pytest.fixture()
def as_user(client: TestClient, user: User) -> TestClient:
    from app.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: user
    return client
```

`StaticPool` is the detail people miss: an in-memory SQLite database normally disappears when the
connection closes, and `TestClient` runs the app on a different connection from your test.
`StaticPool` forces every connection in the process to share the same in-memory database.

```python
# tests/test_decks.py
def test_anonymous_gets_401(client):
    assert client.get("/decks/").status_code == 401


def test_owner_sees_own_decks(as_user, user):
    as_user.post("/decks/", json={"name": "Spanish", "description": "verbs"})
    response = as_user.get("/decks/")
    assert response.status_code == 200
    assert [d["name"] for d in response.json()] == ["Spanish"]


def test_other_users_deck_is_404(as_user, session, user):
    from app.models import Deck

    other = User(email="bob@example.com", hashed_password=hash_password("hunter2hunter2"))
    session.add(other)
    session.commit()
    foreign = Deck(name="Private", owner_id=other.id)
    session.add(foreign)
    session.commit()

    assert as_user.get(f"/decks/{foreign.id}").status_code == 404


def test_password_is_never_returned(as_user):
    body = as_user.post("/auth/signup", json={"email": "c@example.com", "password": "averysecurepw"}).json()
    assert "hashed_password" not in body
    assert set(body) == {"id", "email", "is_active"}


def test_login_sets_httponly_cookie(client, user):
    response = client.post("/auth/login", json={"email": user.email, "password": "hunter2hunter2"})
    assert response.status_code == 200
    assert "access_token" in response.cookies
```

`dependency_overrides` replaces a dependency for the whole app during the test. It is the reason
you should depend on `get_current_user` rather than decoding the cookie inside each handler —
there is nothing to override if the logic is inline.

:::pitfall One Session shared across requests
The tempting shortcut is a module-level `session = SessionLocal()` used by every handler. A SQL
`Session` is not thread-safe, holds a single transaction, and caches identity-mapped objects
forever. With `--workers` (Chapter 29) or any concurrency you get cross-request data leaks,
`InterfaceError: cannot operate on a closed database`, and transactions that never commit or that
commit another user's writes. One session per request, obtained through `Depends` with `yield`,
and nothing else.
:::

:::scenario Random 500s after launch, and an auditor asking about ID enumeration
StudyHub ships with a module-level session and handlers that fetch first and check ownership
after: `deck = session.get(Deck, id)` then `if deck.owner_id != user.id: raise 403`. Two weeks
later: sporadic `InterfaceError` and `MissingGreenlet` errors under real traffic, one user
briefly seeing another user's deck, and a security review flagging that any logged-in user can
enumerate which deck IDs exist.
:::

:::solution Fix the session, then move authorization into the query
1. **Session per request.** Delete the global. Export `get_session()` and `SessionDep` from
   `app/database.py` and change every handler parameter from `session = SessionLocal()` to
   `session: SessionDep`. Because the dependency closes the session after the response, the
   `InterfaceError` disappears by construction.
2. **Authorize in the WHERE clause.** Replace fetch-then-check with
   `select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)` and a single 404
   when `one_or_none()` is `None`. There is no longer a moment where a foreign object is loaded
   into memory, and the status code stops leaking existence.
3. **Load relationships eagerly** with `selectinload(Deck.cards)` so serialization never triggers
   a lazy load outside the session.
4. **Prove it with tests.** Add `test_other_users_deck_is_404` and a test that two overlapping
   requests do not share state. Both failures above were invisible without concurrent or
   cross-user tests — that is the real lesson: authorization bugs and session bugs only show up
   in tests that involve a *second* user.

The general principle: authorization is a query concern, not a branch after the query.
:::

## Key takeaways

- A SQLAlchemy `Session` is scoped to one request via a `yield` dependency; never share it.
- ORM models (`models.py`) describe storage, Pydantic schemas (`schemas.py`) describe the wire,
  and `from_attributes=True` bridges them safely.
- Use SQLAlchemy 2.x `select()`/`session.scalars()`; load collections with `selectinload` to avoid
  N+1 queries during serialization.
- Hash passwords with bcrypt (or `pwdlib`); the response schema must simply omit the hash.
- Put JWTs in `HttpOnly`, `SameSite=Lax`, `Secure` cookies for server-rendered apps, and always
  pass `algorithms=[...]` when decoding.
- Authorize inside the query and return 404 — not 403 — for resources the user cannot see.
- Test against a fresh in-memory database per test and override `get_current_user` to fake auth;
  assert the exact response keys to catch schema leaks.

## Practice

- [ ] Add `POST /decks/{deck_id}/cards` and `GET /decks/{deck_id}/cards` (paginated), both
      restricted to the deck owner.
- [ ] Add a `total` field to the deck list response using `func.count()`, and test that it changes
      when a deck is created.
- [ ] Add `PATCH /decks/{deck_id}` ownership tests: owner gets 200, anonymous gets 401, a second
      user gets 404.
- [ ] Add a `require_active_user` sub-dependency that rejects `is_active=False` with 403, and a
      test that deactivating a user locks them out.
- [ ] Add rate limiting to `POST /auth/login`: after five failed attempts within a minute, return
      429, using a dependency that counts attempts against the email.
- [ ] Write a test that creates two decks with `selectinload` in play and asserts the number of
      SQL statements executed stays constant as decks are added.

## Solutions

:::solution Exercise 1
```python
@router.post("/{deck_id}/cards", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(deck_id: int, payload: CardCreate, session: SessionDep,
                current_user: CurrentUser) -> Card:
    deck = session.scalars(
        select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    ).one_or_none()
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    card = Card(**payload.model_dump(), deck_id=deck.id)
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


@router.get("/{deck_id}/cards", response_model=list[CardRead])
def list_cards(deck_id: int, session: SessionDep, current_user: CurrentUser,
               limit: Annotated[int, Query(ge=1, le=100)] = 50,
               offset: Annotated[int, Query(ge=0)] = 0) -> list[Card]:
    stmt = (
        select(Card)
        .join(Deck)
        .where(Deck.id == deck_id, Deck.owner_id == current_user.id)
        .order_by(Card.id)
        .offset(offset)
        .limit(limit)
    )
    return list(session.scalars(stmt).all())
```
The child resource is authorized through its parent: the `join` plus `Deck.owner_id` means a card
in someone else's deck is indistinguishable from a card that does not exist.
:::

:::solution Exercise 2
```python
class DeckPage(BaseModel):
    items: list[DeckRead]
    total: int
    limit: int
    offset: int


@router.get("/", response_model=DeckPage)
def list_decks(session: SessionDep, current_user: CurrentUser,
               limit: Annotated[int, Query(ge=1, le=100)] = 20,
               offset: Annotated[int, Query(ge=0)] = 0) -> DeckPage:
    items, total = search_decks(session, owner_id=current_user.id, limit=limit, offset=offset)
    return DeckPage(items=items, total=total, limit=limit, offset=offset)
```
```python
def test_total_grows(as_user):
    before = as_user.get("/decks/").json()["total"]
    as_user.post("/decks/", json={"name": "Chemistry"})
    assert as_user.get("/decks/").json()["total"] == before + 1
```
Count with `select(func.count()).select_from(stmt.subquery())` so the `WHERE` clause is reused;
counting `len(items)` would report the page size instead of the result size.
:::

:::solution Exercise 3
```python
def test_owner_can_rename(as_user, user, session):
    deck_id = as_user.post("/decks/", json={"name": "Before"}).json()["id"]
    assert as_user.patch(f"/decks/{deck_id}", json={"name": "After"}).status_code == 200


def test_anonymous_cannot_patch(client):
    assert client.patch("/decks/1", json={"name": "nope"}).status_code == 401


def test_other_user_gets_404(as_user, session):
    other = User(email="eve@example.com", hashed_password=hash_password("hunter2hunter2"))
    session.add(other)
    session.commit()
    foreign = Deck(name="Secret", owner_id=other.id)
    session.add(foreign)
    session.commit()

    response = as_user.patch(f"/decks/{foreign.id}", json={"name": "hacked"})
    assert response.status_code == 404
```
Three different callers, three different outcomes — 401 for "who are you", 404 for "not yours".
Writing all three is what forces the distinction into the code.
:::

:::solution Exercise 4
```python
def require_active_user(current_user: CurrentUser) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive account")
    return current_user


ActiveUser = Annotated[User, Depends(require_active_user)]


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deck(deck_id: int, session: SessionDep, current_user: ActiveUser) -> None:
    ...
```
```python
def test_inactive_user_is_locked_out(client, session, user):
    from app.deps import get_current_user

    user.is_active = False
    session.commit()
    app.dependency_overrides[get_current_user] = lambda: user
    assert client.get("/decks/").status_code == 200      # reading still allowed
    assert client.delete("/decks/1").status_code == 403  # mutating is not
```
This is a legitimate 403: the user is authenticated and known, and the resource is irrelevant.
Composing `ActiveUser` on top of `CurrentUser` is how dependency chains stay readable.
:::

:::solution Exercise 5
```python
import time
from collections import defaultdict

from fastapi import Request

ATTEMPTS: dict[str, list[float]] = defaultdict(list)
_WINDOW = 60.0
_MAX = 5


def check_login_rate(email: str) -> None:
    now = time.monotonic()
    recent = [t for t in ATTEMPTS[email] if now - t < _WINDOW]
    recent.append(now)
    ATTEMPTS[email] = recent
    if len(recent) > _MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts",
            headers={"Retry-After": "60"},
        )


@router.post("/login", response_model=UserRead)
def login(payload: LoginRequest, request: Request, response: Response,
          session: SessionDep) -> User:
    check_login_rate(payload.email)
    ...
```
```python
def test_login_rate_limit(client, user):
    for _ in range(5):
        client.post("/auth/login", json={"email": user.email, "password": "wrong"})
    assert client.post("/auth/login",
                       json={"email": user.email, "password": "wrong"}).status_code == 429
```
An in-process dict is correct only for a single worker; with multiple workers (Chapter 29) move
this to Redis. The point here is the dependency shape: the check runs before password work, so a
flood of bad logins costs almost nothing.
:::

:::solution Exercise 6
```python
import pytest
from sqlalchemy import event

from app.models import Deck, User


@pytest.fixture()
def count_statements(session):
    statements: list[str] = []
    test_engine = session.get_bind()

    def before(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(test_engine, "before_cursor_execute", before)
    yield statements
    event.remove(test_engine, "before_cursor_execute", before)


def test_list_decks_is_constant_statements(as_user, user, session, count_statements):
    for i in range(10):
        session.add(Deck(name=f"Deck {i}", owner_id=user.id))
    session.commit()

    count_statements.clear()
    as_user.get("/decks/")
    first = len(count_statements)

    for i in range(10, 30):
        session.add(Deck(name=f"Deck {i}", owner_id=user.id))
    session.commit()

    count_statements.clear()
    as_user.get("/decks/")
    assert len(count_statements) == first
```
SQLAlchemy's event API lets you count statements without an external profiler. `session.get_bind()`
returns the engine the test session is actually using, so the listener sees test traffic. With
`response_model=DeckRead` the count stays at one; switch the endpoint to `DeckReadWithCards`
without `selectinload` and it grows linearly, because each deck's `cards` triggers its own
`SELECT`.
:::

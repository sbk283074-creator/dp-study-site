---
chapter: 37
part: 6
title: Real-World Scenarios & Solutions
summary: Twenty situations that actually happen on the job — what the symptom looks like, why it happens, and the code that fixes it.
minutes: 90
tags: [recipes, files, debugging, performance, production]
---

Everything before this appendix taught you a feature and then showed you where it fits. This
chapter runs the other way round: here is the mess, now find the feature. Each entry is a
situation a working Python developer hits within their first year — the symptom you would
actually describe to a colleague, followed by the reasoning and the code that resolves it. Read
it once end to end so you know what is in here, then come back when you recognise a symptom.
Nobody memorises this chapter; they grep it.

## Data & files

:::scenario A 12 GB CSV has to be summarised on a 16 GB laptop
You are handed `events_2025.csv` — twelve gigabytes — and asked for revenue by region by
lunchtime. Your first attempt is `data = path.read_text()` or `pandas.read_csv(path)`, the fan
spins up, the machine starts swapping, and either you get `MemoryError` or the whole laptop
freezes. The file is bigger than your RAM, and even when it is not, Python objects are much
bigger than the bytes they came from.
:::

:::solution Never materialise the file — iterate it
`read()` and `readlines()` build one giant string or list. A file object is already an iterator:
it pulls a buffer at a time from the OS and throws the previous buffer away. The fix is to keep
a *running total* instead of a *list of rows*, so memory stays flat no matter how big the input
is.

```python
import csv
import itertools
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


def iter_rows(path: Path, *, encoding: str = "utf-8"):
    """Yield one dict per row. Memory use is constant regardless of file size."""
    with path.open("r", encoding=encoding, newline="") as fh:
        yield from csv.DictReader(fh)


def revenue_by_region(path: Path) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for count, row in enumerate(iter_rows(path), start=1):
        totals[row["region"]] += Decimal(row["amount"])
        if count % 250_000 == 0:
            print(f"  {count:,} rows processed", flush=True)
    return dict(totals)


if __name__ == "__main__":
    print(revenue_by_region(Path("events_2025.csv")))
```

```text
  250,000 rows processed
  500,000 rows processed
  ...
{'EMEA': Decimal('4822113.90'), 'APAC': Decimal('3110880.05')}
```

When you need batches — inserting into a database, say — slice the iterator instead of the file:

```python
def chunks(iterable, size: int):
    """Group an iterator into lists of at most `size` items."""
    it = iter(iterable)
    while batch := list(itertools.islice(it, size)):
        yield batch


for batch in chunks(iter_rows(path), 5_000):
    session.bulk_insert_mappings(Event, batch)
```

With pandas the same idea is `chunksize`, plus `usecols` and `dtype` to stop it guessing:

```python
import pandas as pd

totals = pd.Series(dtype="float64")
for chunk in pd.read_csv(path, chunksize=250_000, usecols=["region", "amount"]):
    totals = totals.add(chunk.groupby("region")["amount"].sum(), fill_value=0)
```

:::pitfall `readlines()` is not the streaming version of `read()`
`readlines()` returns a list of every line — same problem, nicer syntax. Read a file object
directly (`for line in fh`) or use `csv.reader(fh)`. Also remember lines are *delimited*, not
*records*: a quoted CSV field containing a newline will break naive `for line in fh` parsing,
which is why `csv` exists.
:::
:::

:::scenario `UnicodeDecodeError` — but only on Windows
The script works on your Mac and on the Linux server. A colleague on Windows runs the same code
against the same file and gets `UnicodeDecodeError: 'charmap' codec can't decode byte 0xc3 in
position 42`. Nothing about the data changed; only the machine did, because Python's default
text encoding comes from the platform.
:::

:::solution Always name the encoding
On macOS and Linux the default is UTF-8. Windows still defaults to a legacy code page such as
`cp1252`, so every `open()` without an explicit `encoding=` is a coin flip. Check what your
machine thinks:

```python
import locale
print(locale.getpreferredencoding(False))   # 'UTF-8' on macOS/Linux, 'cp1252' on Windows
```

The fix is boring and total: pass `encoding=` at every boundary where bytes become text.

```python
from pathlib import Path

# Reading
text = Path("report.txt").read_text(encoding="utf-8")
with Path("data.csv").open(encoding="utf-8", newline="") as fh:
    ...

# Writing
Path("out.json").write_text(payload, encoding="utf-8")

# csv, json, configparser, sqlite — all take or need an encoding
import csv, json
with Path("data.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

with Path("out.json").open("w", encoding="utf-8") as fh:
    json.dump(rows, fh, ensure_ascii=False)
```

```bash
# Belt and braces: force UTF-8 for the whole process on any platform
PYTHONUTF8=1 python3 report.py
```

Three extra rules save the remaining cases:

- **Excel CSVs** often start with a UTF-8 BOM, which shows up as `\ufeff` glued to your first
  column name. Read those with `encoding="utf-8-sig"`.
- **You do not control the input?** Decide deliberately: `errors="replace"` to keep going with
  `?` characters, `errors="strict"` (the default) to fail loudly. Never leave the choice
  implicit.
- **`subprocess` and HTTP** also decode bytes. Pass `encoding="utf-8", errors="replace"` to
  `subprocess.run`, and prefer `response.text` only when you know the charset;
  `response.content` plus an explicit decode is safer for scraped data.

Add a Ruff or flake8 rule (`flake8-encodings`, Ruff's `W` rules) so this can never regress.
:::

:::scenario The export contains whatever the regional offices typed
Finance sends you `sales_q3.csv`. Dates appear as `2025-03-04`, `04/03/2025`, `4-Mar-2025` and
`""`. Money appears as `"1,234.56"`, `"€1.234,56"`, `"(45.00)"`, `"N/A"` and `" "`. Your parser
throws on row 12, and even when it does not, the numbers it produces are quietly wrong: is
`1,234` one thousand two hundred thirty-four or one point two three four?
:::

:::solution Normalise what you can, reject what you cannot, and report both
The instinct is to make the parser smarter until it swallows everything. Resist it. A parser
that guesses turns data errors into silent financial errors. The professional shape is three
buckets: convert unambiguous values, quarantine ambiguous ones, and emit a report someone signs
off on.

```python
import csv
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%Y", "%Y/%m/%d")
_MONEY_JUNK = re.compile(r"[^\d.,()\-]")


def parse_date(raw: str) -> str | None:
    """Return an ISO date string, or None if the value cannot be trusted."""
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def parse_money(raw: str) -> Decimal | None:
    """Parse currency text. Refuse genuinely ambiguous formats instead of guessing."""
    raw = raw.strip()
    if not raw:
        return None
    negative = raw.startswith("(") and raw.endswith(")")
    cleaned = _MONEY_JUNK.sub("", raw)          # strip €, $, spaces, letters
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            return None                          # European format: ambiguous, reject
        cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        head, _, tail = cleaned.rpartition(",")
        cleaned = f"{head.replace(',', '')}.{tail}" if len(tail) == 2 else cleaned.replace(",", "")
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -value if negative else value


@dataclass
class ParseResult:
    good: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)


def parse_sales(path: Path) -> ParseResult:
    result = ParseResult()
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for line_no, row in enumerate(csv.DictReader(fh), start=2):
            date = parse_date(row.get("date", ""))
            amount = parse_money(row.get("amount", ""))
            if date is None or amount is None:
                result.rejected.append({"line": line_no, **row})
                continue
            result.good.append({"date": date, "amount": amount, "region": row["region"].strip()})
    return result


if __name__ == "__main__":
    outcome = parse_sales(Path("sales_q3.csv"))
    print(f"accepted {len(outcome.good)}, rejected {len(outcome.rejected)}")
    for bad in outcome.rejected[:5]:
        print(f"  line {bad['line']}: date={bad.get('date')!r} amount={bad.get('amount')!r}")
```

```text
accepted 8412, rejected 37
  line 118: date='4-Mar-2025' amount='(45.00)'
  line 402: date='' amount='N/A'
```

Note what line 118 shows: `(45.00)` *was* parsed (parentheses mean negative), so the rejection
came from the date — `%d-%b-%Y` is locale-dependent for the month name, and it failed because
the locale on that machine is not English. That is exactly the kind of thing you want surfaced
in a report rather than guessed at. Ship the rejected rows back to the sender as a CSV; the fix
belongs upstream.
:::

:::scenario The job dies halfway through and leaves a half-written file behind
Your nightly import runs for forty minutes, gets OOM-killed at 3 a.m., and leaves `report.json`
containing `{"totals": {"EMEA": 41` — every downstream job now chokes on invalid JSON. On other
nights a reader opens the file while your script is still writing and sees yesterday's data with
today's timestamp. And on Windows you periodically get `PermissionError` because someone has the
output open in Excel.
:::

:::solution Atomic writes for output, retries for locks, checkpoints for resumes
Three separate problems, three standard tools.

**1. Never write a file in place.** Write to a temporary file in the same directory, fsync it,
then `os.replace()` it over the target. `os.replace` is atomic on POSIX and on Windows: a reader
sees either the old file or the new one, never a half-state.

```python
import json
import os
import tempfile
from pathlib import Path


def atomic_write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
            fh.flush()
            os.fsync(fh.fileno())      # make sure the bytes hit the disk
        os.replace(tmp_name, path)     # atomic swap
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
```

**2. Retry when the file is genuinely locked.** Windows locks files that are open; on POSIX you
are usually fighting an advisory lock or a filesystem that has not settled yet.

```python
import time


def wait_for_file(path: Path, *, timeout: float = 30.0, poll: float = 0.5) -> Path:
    """Block until `path` exists and has stopped changing size."""
    deadline = time.monotonic() + timeout
    last_size = -1
    while time.monotonic() < deadline:
        if path.exists():
            size = path.stat().st_size
            if size == last_size and size > 0:
                return path
            last_size = size
        time.sleep(poll)
    raise TimeoutError(f"{path} never became readable within {timeout}s")
```

**3. Make the job resumable.** Write a checkpoint after every unit of work and skip units that
are already done. Combined with atomic writes, a crash costs you one unit, not forty minutes.

```python
import hashlib


def checkpoint_path(job: str) -> Path:
    return Path(f".state/{job}.json")


def run_import(chunks: list[str], job: str = "nightly") -> None:
    state_file = checkpoint_path(job)
    done = set(json.loads(state_file.read_text())["done"]) if state_file.exists() else set()

    for chunk in chunks:
        key = hashlib.sha256(chunk.encode()).hexdigest()[:16]
        if key in done:
            continue                                   # idempotent: skip finished work
        process(chunk)                                 # must be safe to run exactly once
        done.add(key)
        atomic_write_json(state_file, {"done": sorted(done)})

    atomic_write_json(Path("report.json"), {"chunks": len(done)})
    state_file.unlink(missing_ok=True)                 # clear state only on full success
```

The rule that makes all of this work: **each step must be idempotent.** `process(chunk)` has to
mean "make it so", not "add another one" — use upserts, not inserts.
:::

:::scenario Users can upload files to your app
Your FastAPI endpoint takes an `UploadFile` and does `open(user.filename, "wb").write(data)`.
Within a week someone has uploaded `../../etc/cron.d/evil`, a 4 GB file that exhausts the disk,
and `invoice.pdf` that is actually a Windows executable. The filename is attacker-controlled
input, and you treated it as a path.
:::

:::solution Validate type and size, generate the name, store outside the web root
Four rules, none optional:

1. **Enforce a size limit while streaming**, not after the upload finishes.
2. **Sniff the content** with magic bytes; never trust the extension or the `Content-Type`
   header, both of which the client controls.
3. **Generate the stored name yourself** (UUID + sniffed extension). Keep the original name as
   *metadata* only, and sanitise it before you ever display it.
4. **Store outside the static/web root** and serve through an authorised handler.

```python
import uuid
from pathlib import Path

MAX_BYTES = 10 * 1024 * 1024
CHUNK = 64 * 1024
UPLOAD_DIR = Path("/var/app-data/uploads").resolve()   # NOT inside the static folder

SIGNATURES: list[tuple[bytes, str]] = [
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"\xff\xd8\xff", ".jpg"),
    (b"%PDF", ".pdf"),
    (b"PK\x03\x04", ".zip"),
]


def sniff_extension(header: bytes) -> str | None:
    for magic, ext in SIGNATURES:
        if header.startswith(magic):
            return ext
    return None


def save_upload(fileobj, *, upload_dir: Path = UPLOAD_DIR) -> Path:
    """Stream an upload to disk safely. Raises ValueError on anything suspicious."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    tmp = upload_dir / f".{uuid.uuid4().hex}.part"
    with tmp.open("wb") as out:
        while chunk := fileobj.read(CHUNK):
            written += len(chunk)
            if written > MAX_BYTES:
                out.close()
                tmp.unlink(missing_ok=True)
                raise ValueError("file exceeds 10 MB")
            out.write(chunk)

    header = tmp.open("rb").read(16)
    ext = sniff_extension(header)
    if ext is None:
        tmp.unlink(missing_ok=True)
        raise ValueError("unsupported file type")

    final = upload_dir / f"{uuid.uuid4().hex}{ext}"
    final = final.resolve()
    if not final.is_relative_to(upload_dir):          # belt and braces
        raise ValueError("refusing to write outside the upload directory")
    return tmp.replace(final), written
```

```text
>>> save_upload(open("cat.png", "rb"))
(PosixPath('/var/app-data/uploads/9f1c...png'), 84122)
```

Never build paths by concatenation (`UPLOAD_DIR + "/" + filename`) — that is how `../` escapes
work. Use `pathlib` and verify with `is_relative_to()`. Serve the file back through a route that
checks permissions and sets `Content-Disposition: attachment`, so a stored `.html` or `.svg`
cannot run script in your origin.
:::

## Correctness & debugging

:::scenario The monthly report shows yesterday's data
The report for March is generated at 00:30 UTC on 1 April and attributes a chunk of 31 March
orders to April — or worse, the "monthly total" your finance team sees is consistently off by a
few hundred pounds at each month boundary. Your datetimes have no timezone attached, so "what
month is this?" depends on whatever the server's clock thought.
:::

:::solution Store and compute in UTC; convert only at the human boundary
A naive `datetime` is a wall-clock time with no location. `datetime.utcnow()` — deprecated in
Python 3.12 — hands you a naive object that *looks* like UTC and is therefore a trap: it will be
subtracted from an aware datetime and raise `TypeError`, or compared against local time and be
wrong. Use `datetime.now(timezone.utc)` and `zoneinfo`.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Writing: always UTC, always aware
created_at = datetime.now(timezone.utc)

# Reading back from a DB driver that returns naive UTC (e.g. older SQLite setups)
aware = created_at.replace(tzinfo=timezone.utc)
```

Group by the *business* timezone, not the server's:

```python
from collections import defaultdict

BUSINESS_TZ = ZoneInfo("Europe/London")

def month_key(moment: datetime) -> str:
    """The calendar month in the business's own timezone."""
    return moment.astimezone(BUSINESS_TZ).strftime("%Y-%m")

def revenue_by_month(orders: list[tuple[datetime, float]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for created_at, amount in orders:
        totals[month_key(created_at)] += amount
    return dict(totals)
```

```python
>>> from datetime import datetime, timezone
>>> revenue_by_month([(datetime(2025, 4, 1, 0, 30, tzinfo=timezone.utc), 100.0)])
{'2025-04': 100.0}     # correct: BST is UTC+1, so 00:30Z is 01:30 on 1 April
```

Two more rules that prevent the next incident:

- **Boundaries are exclusive.** Query `WHERE created_at >= :start AND created_at < :end`, never
  `BETWEEN`, which double-counts the instant at midnight.
- **Store instants, render local.** Keep UTC in the database; call `astimezone()` in the
  template or serializer. If you must display an exact instant, use `.isoformat()`, which
  includes the offset and round-trips.

```python
>>> datetime(2025, 4, 1, tzinfo=timezone.utc).isoformat()
'2025-04-01T00:00:00+00:00'
```

:::pitfall DST makes "one day" a lie
Twice a year a local day has 23 or 25 hours. Any arithmetic you do in local time (`+ timedelta(days=1)`)
produces a shifted time-of-day across a DST boundary. Do arithmetic in UTC, then convert for
display.
:::
:::

:::scenario Invoice totals are off by a cent
The line items sum to £1,234.56 but the invoice prints £1,234.55. Nobody can reproduce it
reliably, and it only shows up on certain orders. Your totals are floats, and binary floating
point cannot represent most decimal fractions exactly.
:::

:::solution Use `Decimal` for money, and round once at the boundary
```python
>>> 0.1 + 0.2
0.30000000000000004
>>> sum([0.1] * 10) == 1.0
False
```

Money is decimal and exact. `Decimal` stores base-10 digits and does arithmetic the way an
accountant expects.

```python
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
VAT_RATE = Decimal("0.20")

def invoice_total(lines: list[str], *, discount: str = "0.00") -> Decimal:
    subtotal = sum((Decimal(line) for line in lines), Decimal("0"))
    net = subtotal - Decimal(discount)
    vat = (net * VAT_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    return (net + vat).quantize(CENT, rounding=ROUND_HALF_UP)


>>> invoice_total(["19.99", "5.10", "1200.00"], discount="10.00")
Decimal('1465.31')
```

The details that matter:

- **Construct from strings, never floats.** `Decimal("0.1")` is exact; `Decimal(0.1)` inherits
  the float's error (`0.1000000000000000055511151231257827`).
- **Round at the boundary, not per line.** Quantising every intermediate value compounds
  rounding error. Keep full precision through the calculation and quantise when you store or
  display.
- **Pick a rounding mode and write it down.** Python's default is `ROUND_HALF_EVEN` (banker's
  rounding). Finance usually wants `ROUND_HALF_UP`. Both are defensible; silently using the
  wrong one is not.
- **In the database use `NUMERIC`/`DECIMAL`**, not `REAL`/`FLOAT`, and pass `Decimal` objects
  to the driver.

```python
# FastAPI / Pydantic: keep Decimal all the way to the wire
from pydantic import BaseModel, condecimal

class LineItem(BaseModel):
    amount: condecimal(decimal_places=2)   # validated, not floated
```
:::

:::scenario A test fails about one run in five
CI is red, you rerun it, it goes green. Nobody trusts the suite any more, so nobody looks at it,
and a real bug ships three weeks later. The failing test touches "now", or randomness, or
whatever the previous test left in the database.
:::

:::solution Make time, randomness, and state explicit inputs
A flaky test is almost always a hidden dependency on something global. Find it by running the
test in a loop and in isolation:

```bash
for i in $(seq 1 50); do python3 -m pytest tests/test_billing.py -q || break; done
python3 -m pytest tests/test_billing.py::test_cutoff -q      # alone
python3 -m pytest tests/ -p no:randomly -q                    # in declared order
python3 -m pytest tests/ -q --randomly-seed=12345             # reproduce a random order
```

Then remove the hidden input. Do not monkeypatch `datetime` globally — inject a clock:

```python
# billing.py
from datetime import datetime, time, timezone

def is_after_cutoff(now: datetime, cutoff: time = time(17, 0)) -> bool:
    return now.timetz().replace(tzinfo=None) >= cutoff


# test_billing.py
from datetime import datetime, timezone
from billing import is_after_cutoff

def test_before_cutoff():
    assert is_after_cutoff(datetime(2025, 3, 4, 9, 0, tzinfo=timezone.utc)) is False

def test_after_cutoff():
    assert is_after_cutoff(datetime(2025, 3, 4, 22, 0, tzinfo=timezone.utc)) is True

def test_exactly_at_cutoff():          # the boundary case flaky tests hide
    assert is_after_cutoff(datetime(2025, 3, 4, 17, 0, tzinfo=timezone.utc)) is True
```

The other three usual suspects:

```python
import random

# Randomness — seed it, or inject the rng
def test_shuffle_is_deterministic_with_a_seed():
    rng = random.Random(42)
    items = list(range(10))
    rng.shuffle(items)
    assert items == [1, 0, 4, 9, 3, 8, 2, 5, 6, 7]

# Shared state — every test gets its own database and its own temp dir
import pytest

@pytest.fixture
def db(tmp_path):
    from myapp.db import connect
    conn = connect(tmp_path / "test.sqlite3")
    yield conn
    conn.close()

# Order dependence — never assert on a set's iteration order or on dict ordering
# you did not create. Sort before comparing.
assert sorted(result) == ["a", "b", "c"]
```

If a test still flakes after this, it is telling you about a real race in the code — usually
concurrency, a cache, or a shared module-level object. That is a bug, not a test problem. Quarantine it
with `@pytest.mark.xfail(strict=True)` and a linked ticket; never delete it.
:::

:::scenario One function grew to 400 lines
`process_order()` validates input, looks up the customer, calculates tax, writes to three tables,
sends an email, and logs. It has 14 local variables, five levels of nesting, and everybody is
afraid to touch it. Every new requirement adds another `if` in the middle.
:::

:::solution Extract by responsibility, then split reads from decisions
Do not rewrite it. Extract in small, behaviour-preserving steps, running the tests after each
one.

**Step 1 — extract pure helpers.** Anything that takes values and returns values with no I/O is
trivial to extract and trivial to test:

```python
# before
def process_order(payload):
    ...
    if payload["country"] == "GB":
        tax = subtotal * 0.2
    elif payload["country"] in ("DE", "FR"):
        tax = subtotal * 0.19
    ...

# after
VAT_RATES = {"GB": Decimal("0.20"), "DE": Decimal("0.19"), "FR": Decimal("0.19")}

def tax_for(country: str, subtotal: Decimal) -> Decimal:
    rate = VAT_RATES.get(country, Decimal("0.00"))
    return (subtotal * rate).quantize(CENT, rounding=ROUND_HALF_UP)
```

**Step 2 — separate the repository from the service.** The repository knows *how* data is
stored. The service knows *what the business rule is*. Neither knows about HTTP.

```python
from dataclasses import dataclass
from decimal import Decimal


class OrderRepository:
    """All SQL lives here. Nothing in this class makes business decisions."""

    def __init__(self, session):
        self._session = session

    def get(self, order_id: int) -> "Order | None":
        return self._session.get(Order, order_id)

    def add(self, order: "Order") -> None:
        self._session.add(order)

    def unpaid_for(self, customer_id: int) -> list["Order"]:
        return self._session.scalars(
            select(Order).where(Order.customer_id == customer_id, Order.paid_at.is_(None))
        ).all()


@dataclass(frozen=True)
class OrderTotals:
    subtotal: Decimal
    tax: Decimal
    total: Decimal


class OrderService:
    """Business rules. Talks to the repository and to nothing else persistent."""

    def __init__(self, orders: OrderRepository, mailer, clock):
        self._orders = orders
        self._mailer = mailer
        self._clock = clock

    def place(self, customer_id: int, lines: list[dict]) -> OrderTotals:
        subtotal = sum((Decimal(l["amount"]) for l in lines), Decimal("0"))
        tax = tax_for(self._orders.country_of(customer_id), subtotal)
        order = Order(customer_id=customer_id,
                      total=subtotal + tax,
                      created_at=self._clock())
        self._orders.add(order)
        self._mailer.send_receipt(customer_id, order.id)
        return OrderTotals(subtotal, tax, subtotal + tax)
```

**Step 3 — the function becomes a coordinator.** The endpoint is now four lines, and every
piece is testable without a database, an SMTP server, or a clock:

```python
def place_order(payload, session):
    return OrderService(OrderRepository(session), mailer, datetime.now).place(
        payload["customer_id"], payload["lines"]
    )
```

The signal you are done: you can read the top-level function aloud in one breath and it describes
the business process, not the mechanics.
:::

:::scenario Your logs tell you nothing
Production misbehaves. You open the log file and find `INFO: something went wrong` and a
scattered handful of `print()` statements — no timestamp, no module, no traceback, no way to tell
which of the 400 concurrent requests produced which line.
:::

:::solution Structured, levelled, contextual logging — and `logger.exception` for errors
```python
# main.py — configure ONCE, at the entry point, not in library modules
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)
```

Libraries should never configure logging; they just `logging.getLogger(__name__)` and emit. That
lets the application decide where logs go.

Add a correlation ID so you can follow one request through the noise. `contextvars` is the right
tool because it is per-task and therefore safe under `asyncio`:

```python
import contextvars
import json
import logging

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


handler = logging.StreamHandler()
handler.addFilter(RequestIdFilter())
handler.setFormatter(JsonFormatter())
logging.getLogger().handlers = [handler]
```

```python
# In a request handler
token = request_id.set("req-7fa1")
try:
    log.info("placing order", extra={"customer": 41, "lines": 3})
    ...
except Exception:
    log.exception("order failed")     # logs message + full traceback at ERROR
    raise
finally:
    request_id.reset(token)
```

```text
{"ts": "2025-03-04T09:12:03+0000", "level": "INFO", "logger": "app.orders", "request_id": "req-7fa1", "msg": "placing order"}
{"ts": "2025-03-04T09:12:03+0000", "level": "ERROR", "logger": "app.orders", "request_id": "req-7fa1", "msg": "order failed", "exc": "Traceback ..."}
```

Level discipline, because otherwise levels are meaningless:

- `DEBUG` — detail useful only while developing a specific problem.
- `INFO` — a business event happened (order placed, job started).
- `WARNING` — something is off but we coped (retry succeeded, cache miss storm).
- `ERROR` — a request or job failed; someone should look.
- `CRITICAL` — the process cannot continue.

:::pitfall Never f-strings in log calls
`log.info(f"user {u}")` builds the string even when INFO is disabled, and it is unsearchable.
Use lazy formatting: `log.info("user %s", u)` — and pass structured fields via `extra=`.
:::
:::

## Performance & scale

:::scenario The dashboard takes 30 seconds to load
It renders 200 orders with the customer name next to each. Locally with 20 rows it is instant.
You enable SQL echo and discover 201 queries: one for the orders, then one per order to fetch its
customer. This is the classic N+1.
:::

:::solution Load the relationship up front, or aggregate in the database
```python
# N+1 — one query per row. Dies at scale.
orders = session.scalars(select(Order).limit(200)).all()
for order in orders:
    print(order.customer.name)          # lazy load, one SELECT each
```

**Fix 1 — eager load.** `selectinload` issues one extra `SELECT ... WHERE id IN (...)` for the
whole collection, which is nearly always what you want for a "list" view:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

stmt = (
    select(Order)
    .options(selectinload(Order.customer))   # 2 queries total, not 201
    .order_by(Order.created_at.desc())
    .limit(200)
)
orders = session.scalars(stmt).all()
for order in orders:
    print(order.customer.name)               # already loaded, no query
```

`joinedload` is the alternative when you are filtering on the related table and the join is
one-to-one or many-to-one; `selectinload` is safer for collections because it does not
multiply rows.

**Fix 2 — let the database do the maths.** If the page only needs totals, never load rows at
all. A dashboard showing revenue per month is one aggregate query:

```python
from sqlalchemy import func, select

stmt = (
    select(
        func.date_trunc("month", Order.created_at).label("month"),
        func.count(Order.id).label("orders"),
        func.sum(Order.total).label("revenue"),
    )
    .where(Order.created_at >= "2025-01-01")
    .group_by("month")
    .order_by("month")
)
rows = session.execute(stmt).all()
```

```text
[(datetime(2025, 1, 1), 1841, Decimal('221004.55')), (datetime(2025, 2, 1), 2010, Decimal('243881.10'))]
```

Then measure, because intuition about performance is wrong more often than it is right:

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {(time.perf_counter() - start) * 1000:.1f} ms")
```

```python
with timer("dashboard query"):
    rows = session.execute(stmt).all()
```

Add indexes that match your `WHERE` and `ORDER BY` (`CREATE INDEX ... ON orders (created_at)`),
cache anything that does not need to be real-time, and only then consider async or a queue.
:::

:::scenario An API you depend on starts returning 429
Your nightly sync suddenly fails with `429 Too Many Requests`. You are calling a partner API in a
loop, they introduced a rate limit, and your job now gets a burst of failures and then dies.
Retrying immediately makes it worse — you are hammering a service that is already asking you to
stop.
:::

:::solution Exponential backoff with jitter, honour `Retry-After`, and cache what you can
```python
import random
import time

import requests


def get_json(url: str, *, attempts: int = 6, base: float = 0.5, cap: float = 30.0,
             session: requests.Session | None = None) -> dict:
    """GET with exponential backoff + full jitter. Raises after the last attempt."""
    http = session or requests.Session()
    last_error: Exception | None = None

    for attempt in range(attempts):
        try:
            response = http.get(url, timeout=10)
            if response.status_code == 429:
                # Respect the server's own instruction when it gives one
                delay = float(response.headers.get("Retry-After", 0)) or min(cap, base * 2 ** attempt)
                time.sleep(random.uniform(delay / 2, delay))     # jitter around it
                continue
            if response.status_code >= 500:
                time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))   # full jitter
                continue
            response.raise_for_status()
            return response.json()
        except requests.Timeout as exc:
            last_error = exc
            time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))

    raise RuntimeError(f"{url} failed after {attempts} attempts") from last_error
```

Why jitter: if 200 workers all back off for exactly 1, 2, 4 seconds, they retry *together* and
recreate the spike. Randomising the delay spreads the load; "full jitter" (uniform between 0 and
the computed delay) is the simplest scheme that works.

**Reduce the number of calls** — the cheapest request is the one you do not make:

```python
import time
from functools import wraps

def ttl_cache(seconds: float):
    """Memoise a zero-argument-looking call for `seconds`. Good enough for sync jobs."""
    def decorator(fn):
        store: dict[tuple, tuple[float, object]] = {}

        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            hit = store.get(key)
            if hit and time.monotonic() - hit[0] < seconds:
                return hit[1]
            value = fn(*args, **kwargs)
            store[key] = (time.monotonic(), value)
            return value
        return wrapper
    return decorator


@ttl_cache(300)
def exchange_rate(base: str, quote: str) -> float:
    return get_json(f"https://api.example.com/rates?base={base}&quote={quote}")["rate"]
```

Also: reuse a `requests.Session()` (it pools TCP connections and is dramatically faster than
`requests.get` in a loop), send `If-None-Match`/`If-Modified-Since` if the API supports it, and
if the API offers a bulk endpoint, use it instead of N calls.
:::

:::scenario The third-party service is down entirely
The payments provider is returning 503. Every request to your checkout now hangs for 30 seconds
before failing, your worker pool is saturated with waiting threads, and the whole site —
including pages that have nothing to do with payments — becomes unresponsive. A slow dependency
is worse than a dead one.
:::

:::solution Timeouts everywhere, a circuit breaker, and graceful degradation
**1. Timeouts are not optional.** A call without a timeout is an unbounded resource leak:

```python
import requests

response = requests.post(url, json=payload, timeout=(3.05, 10))   # (connect, read)
```

**2. Stop calling a service that is failing.** A circuit breaker fails fast while the dependency
recovers, then probes it:

```python
import time
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    CLOSED = "closed"        # normal
    OPEN = "open"            # failing: reject immediately
    HALF_OPEN = "half_open"  # probing: let one call through


@dataclass
class CircuitBreaker:
    threshold: int = 5
    cooldown: float = 60.0
    failures: int = 0
    opened_at: float | None = None
    state: State = State.CLOSED

    def allows(self) -> bool:
        if self.state is State.OPEN and time.monotonic() - self.opened_at > self.cooldown:
            self.state = State.HALF_OPEN
        return self.state is not State.OPEN

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None
        self.state = State.CLOSED

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold:
            self.state = State.OPEN
            self.opened_at = time.monotonic()
```

**3. Serve the last known good value.** Stale data beats an error page for things like exchange
rates, feature flags, and stock counts:

```python
import json
from pathlib import Path


def fetch_rate(breaker: CircuitBreaker, cache_path: Path = Path("rate.json")) -> float:
    if not breaker.allows():
        return json.loads(cache_path.read_text())["rate"]      # degraded, but alive

    try:
        rate = get_json("https://api.example.com/rate")["rate"]
    except Exception:
        breaker.record_failure()
        if cache_path.exists():
            return json.loads(cache_path.read_text())["rate"]  # cached last-good
        raise

    breaker.record_success()
    atomic_write_json(cache_path, {"rate": rate, "fetched_at": time.time()})
    return rate
```

```text
>>> breaker = CircuitBreaker(threshold=2, cooldown=5)
>>> fetch_rate(breaker)
1.0842
>>> # provider dies...
>>> fetch_rate(breaker)      # serves cached value, no 30-second hang
1.0842
```

Always make degradation *visible*: return the stale value with a flag or a banner ("rates as of
09:12"), and emit a `WARNING` with the breaker's state so your alerting sees it. A circuit
breaker that silently hides an outage is how outages last for a week.
:::

:::scenario A script must never run twice at once
Your ETL job runs every five minutes from cron. When one run takes longer than five minutes, a
second one starts on top of it. They both read the same pending rows, both write the same output,
and you get duplicated records and a corrupted file.
:::

:::solution Take an exclusive lock, or make the claim in the database
The portable approach is a lock file with an advisory lock. On POSIX, `flock` is released
automatically when the process dies — including when it is killed — so there is no stale-lock
cleanup problem:

```python
import contextlib
import fcntl
import os
from pathlib import Path


@contextlib.contextmanager
def single_instance(name: str, lock_dir: Path = Path("/var/lock")):
    """Fail fast if another process already holds this lock."""
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{name}.lock"
    with lock_path.open("w", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"{name} is already running") from exc
        try:
            fh.write(str(os.getpid()))
            fh.flush()
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    with single_instance("etl"):
        run_import()
```

`LOCK_NB` makes it non-blocking: the second run exits with a clear message instead of queuing up
behind the first and stampeding when it finally gets the lock. Drop `LOCK_NB` if you genuinely
want the runs to queue.

Windows has no `fcntl`. For cross-platform code use `portalocker` (`pip install portalocker`),
which wraps `msvcrt.locking` and `fcntl` behind one API.

**The better fix when a database is involved:** claim the work in the database, because that
survives multiple machines. Add a `jobs` row with a unique constraint and let the loser lose:

```python
import sqlalchemy as sa

try:
    session.execute(sa.text("INSERT INTO jobs (name, started_at) VALUES (:n, now())"), {"n": "etl"})
    session.commit()
except sa.exc.IntegrityError:
    session.rollback()
    print("another run already holds the job", flush=True)
    raise SystemExit(0)
```

Postgres users can go further and use `pg_advisory_lock()`, which needs no table at all.
:::

:::scenario You have to change a database column in production, without downtime
`users.email` is `VARCHAR(64)` and needs to be `VARCHAR(320)`, or you are splitting
`users.name` into `first_name` and `last_name`. The table has 40 million rows and the site must
stay up. Running `ALTER TABLE` locks it for minutes and every request times out.
:::

:::solution Expand, backfill, dual-write, switch, contract
Never do it in one step. Each of these steps is independently deployable and reversible:

```sql
-- Step 1: EXPAND — add the new column. Nullable, no default → instant on modern
-- MySQL/Postgres. Ship the migration with zero code changes.
ALTER TABLE users ADD COLUMN email_new VARCHAR(320) NULL;

-- Step 2: BACKFILL in batches from a script (see below). Do not UPDATE 40M rows in one
-- transaction: it holds locks and blows up the WAL / binlog.
UPDATE users SET email_new = email WHERE email_new IS NULL AND id BETWEEN :lo AND :hi;

-- Step 3: DUAL-WRITE — deploy code that writes BOTH columns and reads the OLD one.
-- Step 4: SWITCH READS — deploy code that reads the NEW column, still writing both.
-- Step 5: CONTRACT — once you are confident, stop writing the old column, then drop it
--         (drop is metadata-only on Postgres; still needs care elsewhere).
-- ALTER TABLE users DROP COLUMN email;
```

The backfill script — resumable, batched, with a checkpoint:

```python
import sqlalchemy as sa

BATCH = 5_000


def backfill(engine) -> None:
    with engine.begin() as conn:
        last = conn.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM users WHERE email_new IS NOT NULL")).scalar()
        total = conn.execute(sa.text("SELECT COALESCE(MAX(id), 0) FROM users")).scalar()

    while last < total:
        lo, hi = last + 1, last + BATCH
        with engine.begin() as conn:
            conn.execute(
                sa.text("UPDATE users SET email_new = email "
                        "WHERE email_new IS NULL AND id BETWEEN :lo AND :hi"),
                {"lo": lo, "hi": hi},
            )
        last = hi
        print(f"backfilled up to {last:,} / {total:,}", flush=True)
```

Rules that keep this safe:

- **Every step must work with the previous version of the code deployed.** That is what makes
  rollback safe.
- **Add, never rename, in one release.** Renaming means old code breaks the instant the
  migration lands.
- **Backfill off-peak and throttle.** A slow backfill that finishes is better than a fast one
  that triggers replication lag.
- **Verify before you contract:** `SELECT COUNT(*) FROM users WHERE email_new IS NULL AND email IS NOT NULL`
  must be zero.
- **For very large or long jobs, use a real migration tool** (Alembic for SQLAlchemy, Django
  migrations) and add explicit `op.execute()` batching rather than relying on defaults.
:::

## Working with other people / production

:::scenario The same code has to run locally, in staging, and in production
Hard-coded database URLs, a `DEBUG = True` that somebody forgot, and a settings file that
different people edit differently. It works on your machine and 500s in production because
`DATABASE_URL` points at localhost.
:::

:::solution One typed settings object, populated from the environment
Configuration is the one thing that must differ between environments, so it belongs *outside*
the code — in environment variables (the twelve-factor rule) — and it must be validated at
startup, not discovered at 3 a.m.

```python
# settings.py
from functools import lru_cache

from pydantic import Field, PostgresDsn, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",          # local convenience only; never committed
        env_file_encoding="utf-8",
        env_prefix="APP_",        # APP_DATABASE_URL, APP_DEBUG, ...
        extra="ignore",
    )

    environment: str = Field(default="dev", pattern="^(dev|staging|prod)$")
    database_url: PostgresDsn
    debug: bool = False
    log_level: str = "INFO"
    api_key: str = Field(min_length=1)          # required: startup fails if absent
    max_workers: int = Field(default=4, ge=1, le=64)


@lru_cache
def get_settings() -> Settings:
    """Cached so the process reads and validates the environment exactly once."""
    return Settings()
```

```python
# main.py
import logging
import sys

def main() -> int:
    try:
        settings = get_settings()
    except ValidationError as exc:
        print(f"bad configuration:\n{exc}", file=sys.stderr)
        return 2                                  # fail fast, loudly, at startup

    logging.basicConfig(level=settings.log_level)
    run(settings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

```bash
# dev — .env (git-ignored) holds the defaults
APP_DATABASE_URL=postgresql://localhost/app_dev
APP_API_KEY=dev-key

# prod — the platform injects real values
APP_ENVIRONMENT=prod APP_DATABASE_URL=postgresql://... APP_API_KEY=... python3 main.py
```

Why this shape:

- **It fails at startup, not at first use.** A missing `API_KEY` crashes in the first 50 ms with
  a message naming the variable, instead of the first time a user hits that code path.
- **Types are enforced.** `"true"`, `"1"`, `"yes"` all become booleans; `max_workers=999` is
  rejected by `le=64`.
- **`.env` is for development only.** Commit `.env.example` with the keys and dummy values;
  git-ignore `.env`. Production values go in your platform's secret store.
- **One import, no globals module.** `get_settings()` is cached, so importing it in twenty places
  costs nothing and tests can `get_settings.cache_clear()` and monkeypatch `os.environ`.
:::

:::scenario A cron job silently stopped working
The nightly report has not arrived for a week and nobody noticed until a customer asked. You run
the command by hand and it works perfectly. The crontab entry is `python3 report.py` — and cron
does not have your shell's PATH, your working directory, or your environment variables.
:::

:::solution Give cron nothing to guess: absolute paths, a log file, and a non-zero exit on failure
Cron runs with a minimal environment (`PATH=/usr/bin:/bin`, no profile, `HOME` often unset) and
its current directory is not your project. Anything relative — `python3`, a config filename, a
virtualenv — is a guess.

```bash
# crontab -e
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
MAILTO=oncall@example.com

# m h dom mon dow  command
17 2 * * * cd /srv/reports && /srv/reports/.venv/bin/python3 /srv/reports/report.py >> /var/log/reports/cron.log 2>&1
```

That single line contains four of the five fixes: absolute interpreter (the venv one), absolute
script path, `cd` to the project, and stdout *and* stderr redirected to a log file. Without
`2>&1` the traceback goes to cron's mail, which usually goes nowhere.

The fifth fix is in the script: log to a file and exit non-zero on failure.

```python
# report.py
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("/var/log/reports")          # absolute on purpose


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_DIR / "report.log", maxBytes=5_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    return logging.getLogger("report")


def main() -> int:
    log = configure_logging()
    log.info("job started")
    try:
        build_report()
    except Exception:
        log.exception("report failed")      # traceback lands in the file
        return 1                            # non-zero so cron/MAILTO notices
    log.info("job finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**A successful exit code is not proof the job ran.** For anything that matters, add a heartbeat
("dead man's switch"): ping a monitoring URL at the end of every successful run, and alert if the
ping has not arrived within 25 hours.

```python
import os
import urllib.request

def heartbeat() -> None:
    url = os.environ.get("HEALTHCHECK_URL")
    if not url:
        return
    try:
        urllib.request.urlopen(url, timeout=10).read()
    except OSError as exc:
        logging.getLogger("report").warning("heartbeat failed: %s", exc)
```

Under systemd, `Type=oneshot` plus `OnFailure=` and `Persistent=true` gives you the same
guarantees with better logs (`journalctl -u report.service`).
:::

:::scenario A secret was committed to git
You pushed an AWS key in `config.py`. It has been in the repository for three weeks, the
repository is public, and someone has already emailed you about bots scanning it. Your instinct
is to delete the line and push again.
:::

:::solution Revoke first, then rewrite history — never the other way round
**Step 1 — rotate the credential now.** Deleting the line does nothing: the commit is still in
history, and automated scrapers find new keys in minutes. Disable the key at the provider *before*
you touch git. A rewritten history with a live key is still a live key in someone's clone.

**Step 2 — purge it from history.** `git filter-repo` is the maintained tool (`git filter-branch`
is deprecated and slow):

```bash
python3 -m pip install git-filter-repo

# Replace the secret with a marker everywhere in history
git filter-repo --replace-text <(echo 'AKIAIOSFODNN7EXAMPLE==>***REMOVED***')

# Or remove a whole file that should never have been committed
git filter-repo --path config.py --invert-paths
```

**Step 3 — coordinate the force push.** Rewriting history changes every commit hash, so every
collaborator must re-clone or `git fetch --all && git reset --hard origin/main`. Warn the team
*first*, and do it in a window where nobody has work in flight.

```bash
git push --force-with-lease --all
git push --force-with-lease --tags
```

**Step 4 — make it impossible to repeat.** Add a pre-commit hook that scans before every commit:

```bash
python3 -m pip install pre-commit detect-secrets
detect-secrets scan > .secrets.baseline
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-added-large-files
      - id: end-of-file-fixer
```

```bash
pre-commit install        # runs on every git commit
```

**Step 5 — fix the config shape.** Secrets never belong in the repo. Read them from the
environment (see the settings scenario above), and commit only a template:

```bash
# .gitignore
.env
*.pem
secrets/

# .env.example  (committed, with harmless dummy values)
APP_DATABASE_URL=postgresql://localhost/app_dev
APP_API_KEY=replace-me
```

Also check GitHub/GitLab's own secret scanning and push protection — both will block a known
secret pattern from being pushed at all, which is a far better outcome than finding it later.
:::

:::scenario Two packages require conflicting versions of the same library
You install a new dependency and everything breaks: `ERROR: pip's dependency resolver ...
package A requires pydantic<2.0, but you have pydantic 2.6`. You "fix" it by force-reinstalling,
and now an unrelated feature fails at runtime with an import error.
:::

:::solution One virtualenv per project, pinned dependencies, and a constraints file
The root cause is installing everything into one interpreter. Each project gets its own
environment:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

Then find out *who* wants the old version, instead of guessing:

```bash
python3 -m pip install pipdeptree
pipdeptree --packages pydantic
pipdeptree --warn fail             # CI: fail the build on conflicts
```

```text
pydantic==2.6.4
├── fastapi[all]==0.110.0 [requires: pydantic>=1.7.4,<3.0.0,!=2.0.0,...]
└── legacy-sdk==0.4.2 [requires: pydantic<2.0.0]
```

Now you can make a real decision. In order of preference:

1. **Upgrade the offender.** `legacy-sdk` may have a release that supports pydantic v2.
2. **Replace it.** A forty-line client you own beats a dead dependency.
3. **Isolate it.** If it is a CLI tool rather than a library, install it with `pipx` so it never
   shares an environment with your project: `pipx install legacy-sdk-tool`.
4. **Pin deliberately, in two files.** `requirements.in` is what *you* chose;
   `requirements.txt` is the fully resolved, fully pinned result.

```text
# requirements.in  — direct dependencies, loose
fastapi>=0.110
sqlalchemy>=2.0
httpx

# constraints.txt  — versions we refuse to move past, and why
pydantic<3.0            # fastapi 0.110 and legacy-sdk both tested against 2.x
numpy<2.0               # pandas 1.5 ABI
```

```bash
python3 -m pip install pip-tools
pip-compile requirements.in -o requirements.txt     # resolves the whole tree once
python3 -m pip install -r requirements.txt -c constraints.txt
pip-compile --upgrade requirements.in               # deliberate upgrade, reviewable diff
```

Never run `pip install <pkg>` and then `pip freeze > requirements.txt` on a polluted environment —
you will pin every experiment you ever ran. And never `pip install --force-reinstall` to resolve a
conflict; it produces an environment that pip thinks is fine and Python knows is broken. Modern
alternatives such as `uv` resolve the same problem faster and will refuse to install a genuinely
unsatisfiable set, which is the behaviour you want.
:::

:::scenario A non-technical colleague needs to run your script
You wrote `cleanup.py` and it saved everyone an hour a week. To use it, a colleague must open a
terminal, activate the venv, remember that the argument order is `input output`, and know that
the third positional argument is optional. In practice they ask you to run it, which means the
script saved nobody any time.
:::

:::solution Make one command that cannot easily be misused, and document it in six lines
```python
#!/usr/bin/env python3
"""cleanup.py — tidy a sales export into a spreadsheet-ready CSV.

Usage:
    python3 cleanup.py sales.csv
    python3 cleanup.py sales.csv -o clean.csv --dry-run
"""
import argparse
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a messy sales export (dates, currency, blanks).",
        epilog="Example: python3 cleanup.py sales.csv -o clean.csv",
    )
    parser.add_argument("input", type=Path, help="path to the raw CSV export")
    parser.add_argument("-o", "--output", type=Path,
                        help="where to write the result (default: alongside the input)")
    parser.add_argument("--region", default="EMEA", help="region label to stamp on each row")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would change without writing anything")
    parser.add_argument("-v", "--verbose", action="store_true", help="explain each step")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input.exists():
        print(f"Could not find {args.input}. Check the path and try again.", file=sys.stderr)
        return 1

    output = args.output or args.input.with_name(f"{args.input.stem}-clean{args.input.suffix}")

    try:
        result = parse_sales(args.input)          # from the parsing scenario above
    except Exception as exc:                      # last resort: no traceback for humans
        print(f"Sorry — {args.input} could not be read: {exc}", file=sys.stderr)
        return 1

    print(f"{len(result.good)} rows cleaned, {len(result.rejected)} need a human")
    if args.dry_run:
        print("Dry run — nothing was written.")
        return 0

    write_clean_csv(output, result.good)
    print(f"Written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

The details that make it usable by someone who does not code:

- **Sensible defaults.** Only `input` is required; the output path is derived.
- **`type=Path`** so argparse reports "invalid Path value" rather than your code crashing on a
  string.
- **`--dry-run`** on anything that writes or deletes. It is the difference between trust and fear.
- **Plain-English errors, `return 1`.** A traceback is noise to a non-programmer; exit codes let
  the next tool in the chain react.
- **The docstring is the help text.** `python3 cleanup.py --help` now prints the usage example.

Then give them exactly one command. On macOS, a double-clickable file:

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1
./.venv/bin/python3 cleanup.py "$@"
```

```bash
chmod +x run-cleanup.command     # .command opens in Terminal when double-clicked
```

On Windows, `run-cleanup.bat` with `.\.venv\Scripts\python.exe cleanup.py %*`. And a README that
is not filler — six lines, zero adjectives:

```text
# Sales cleanup

Takes the raw export from the finance system and produces a clean CSV.

1. Put the export next to this file, named sales.csv
2. Double-click run-cleanup.command (macOS) or run-cleanup.bat (Windows)
3. Send the sales-clean.csv that appears

It will never modify the original file. Run with --dry-run to preview.
Questions: ask Lucas. Common problems: "Could not find sales.csv" means the
file is not in this folder, or is still named export (1).csv.
```
:::

## Key takeaways

- Big files are handled by iterating and aggregating, never by `read()`; gold output with `os.replace()` after writing a temp file.
- Every `open()` gets an explicit `encoding=`; Windows defaults to a legacy code page and will decode your UTF-8 differently.
- Money is `Decimal` constructed from strings; quantize once, at the boundary, with a declared rounding mode.
- Instants are stored as timezone-aware UTC and converted with `zoneinfo` only for humans; query ranges are half-open (`>=` / `<`).
- Flaky tests come from hidden inputs — inject the clock and the RNG, isolate state with `tmp_path`, never assert on unordered iteration.
- N+1 queries are fixed with `selectinload` or by aggregating in the database; measure before and after with `time.perf_counter()`.
- Any call over a network needs a timeout, exponential backoff with jitter, and a circuit breaker plus cached last-good for when the dependency dies.
- Long jobs are checkpointed and idempotent; jobs that must not overlap take an advisory lock or claim a row in the database.
- Schema changes ship as expand → backfill → dual-write → switch → contract, one reversible deploy per step.
- Config comes from the environment through one validated settings object; secrets are rotated before history is rewritten, and prevented by a pre-commit scanner.

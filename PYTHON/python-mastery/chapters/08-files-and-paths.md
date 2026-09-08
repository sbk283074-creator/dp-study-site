---
chapter: 8
part: 1
title: Files, Paths & Persistence
summary: Read and write files safely with pathlib and with-blocks, persist structured data as CSV and JSON, and stop losing work to relative paths and half-written files.
minutes: 40
tags: [pathlib, files, csv, json, encoding, atomic-write]
---

Variables live as long as the program does; a file outlives it. Every real application eventually
has to remember something — a saved game, a config file, a cache of API responses, a list of users.
That means paths, file handles, encodings, and a serialisation format. Get these four right and
Chapter 23's TaskForge CLI and Chapter 30's StudyHub web app are both just this chapter scaled up.

## `pathlib.Path`: paths as objects

Forget `os.path` and string concatenation. `Path` is the modern default, and the `/` operator
joins path segments without you ever typing a slash.

```python
from pathlib import Path

data_dir = Path("data")
file = data_dir / "journal" / "2026-09-07.json"
print(file)
```
```text
data/journal/2026-09-07.json
```

The parts you will use constantly:

```python
p = Path("/Users/ada/notes/todo.txt")

p.name        # 'todo.txt'      — filename with extension
p.stem        # 'todo'          — filename without extension
p.suffix      # '.txt'          — final extension
p.parent      # PosixPath('/Users/ada/notes')
p.parts       # ('/', 'Users', 'ada', 'notes', 'todo.txt')

q = p.with_suffix(".md")              # PosixPath('/Users/ada/notes/todo.md')
q = p.with_name("done.md")            # same folder, different file
home = Path.home() / "projects"       # cross-platform home directory
```

Checking and creating:

```python
p.exists()            # True or False
p.is_file()           # exists AND is a regular file
p.is_dir()            # exists AND is a directory
Path("out").mkdir(parents=True, exist_ok=True)   # make it, no error if it already exists
```

`parents=True` creates missing intermediate directories; `exist_ok=True` stops the "directory
already exists" error. Those two keywords together are what you want almost every time.

Finding files:

```python
Path("logs").glob("*.txt")       # matching files directly inside logs/
Path("logs").rglob("*.txt")      # recursive — ** means "any depth"
sorted(Path("src").rglob("*.py"))
```

Both return generators, so wrap them in `list()` or `sorted()` when you need to see the results.

### Read and write in one call

For small files, skip `open()` entirely:

```python
p = Path("notes.txt")
p.write_text("first line\nsecond line\n", encoding="utf-8")
text = p.read_text(encoding="utf-8")
print(text)
```

Pass `encoding="utf-8"` explicitly. Python guesses the default from your operating system, which
means the same code reads fine on your laptop and produces mojibake — or crashes — on a colleague's
machine or a Linux server. Always name the encoding; Chapter 17 revisits this with dates and
numbers.

## `with open(...)` and why you always use it

When you need streaming access — big files, appending, binary data — use `open()` inside a `with`
statement.

```python
with open("data/notes.txt", "r", encoding="utf-8") as f:
    contents = f.read()
# the file is closed here, even if an exception was raised
```

`with` guarantees the file closes when the block ends, including when the code inside blows up.
Without it, an exception leaves the file handle open: on Windows the file becomes undeletable, on
Linux you leak a descriptor per call, and with writing you risk buffered data never reaching disk.
This is the context manager pattern, covered properly in Chapter 14.

### Modes

| Mode | Meaning |
| --- | --- |
| `"r"` | Read (default). Error if the file does not exist. |
| `"w"` | Write. **Truncates the file to zero bytes** first. |
| `"a"` | Append. Creates the file if missing; writes go to the end. |
| `"x"` | Exclusive create. Fails if the file already exists. |
| `"b"` | Binary mode — add it: `"rb"`, `"wb"`. No encoding, bytes in/out. |
| `"+"` | Read *and* write — `"r+"`, `"w+"`. Rarely worth the complexity. |

:::danger `"w"` erases before you write
Opening with `"w"` empties the file the instant you open it, before a single byte is written. If
your code then raises an exception, the old contents are gone. Use `"a"` to append, `"x"` to create
only if absent, or write to a temporary file and replace (see the atomic write pattern below).
:::

## Reading: line by line versus `read()`

`read()` pulls the entire file into memory as one string. Fine for a config file, catastrophic for
a 4 GB log. Iterate the file object instead — it hands you one line at a time and barely uses
memory:

```python
with open("server.log", encoding="utf-8") as f:
    for line in f:                 # streaming, one line at a time
        if "ERROR" in line:
            print(line.rstrip())
```

`readlines()` returns a list of all lines, and `readline()` returns one — you will use neither
often. Note that each `line` still ends with `\n`, which is why `rstrip()` or `strip()` shows up
constantly when parsing.

## CSV: spreadsheets in text form

CSV is the format Excel and every data tool on earth can open. Always use the `csv` module rather
than splitting on commas — quoted fields containing commas will break naive parsing.

```python
import csv
from pathlib import Path

rows = [
    {"name": "ada", "role": "engineer", "commits": 142},
    {"name": "grace", "role": "admiral", "commits": 88},
]

with open("people.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "role", "commits"])
    writer.writeheader()
    writer.writerows(rows)
```

Two details matter: `newline=""` is **required** when writing CSV on all platforms or you get
blank lines between rows, and `DictWriter` needs `fieldnames` up front.

Reading it back:

```python
with open("people.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["name"], int(row["commits"]))
```
```text
ada 142
grace 88
```

`DictReader` yields dicts keyed by the header row. Everything arrives as a **string** — convert
with `int()` or `float()` as needed. If you don't need the headers, `csv.reader` yields plain lists.
Chapter 19 takes this further with SQLite and SQLAlchemy.

## JSON: the format everything speaks

JSON is what APIs return, what config files are written in, and what Chapter 18 will fetch over
HTTP. Four functions, and the `s` tells you whether it deals in strings:

| Function | Does |
| --- | --- |
| `json.dumps(obj)` | object → JSON **string** |
| `json.loads(text)` | JSON string → object |
| `json.dump(obj, f)` | object → **file** |
| `json.load(f)` | file → object |

```python
import json

config = {"host": "localhost", "port": 8000, "debug": True, "tags": ["web", "api"]}

text = json.dumps(config)                          # compact
pretty = json.dumps(config, indent=2, sort_keys=True)
print(pretty)
```
```text
{
  "debug": true,
  "host": "localhost",
  "port": 8000,
  "tags": [
    "api",
    "web"
  ]
}
```

`indent=2` makes it human-readable and diff-friendly; `ensure_ascii=False` keeps non-Latin
characters as real characters instead of `\uXXXX` escapes (use it whenever humans will read the
file).

:::note JSON only knows a few types
JSON handles dicts, lists, strings, numbers, booleans, and `None`. A Python `tuple` becomes a
list, a `set` raises `TypeError: Object of type set is not JSON serializable`, and a `datetime`
raises too. Convert to something JSON understands first — `tuple` → `list`, `set` → `sorted(list)`,
`datetime` → `isoformat()` string. Chapter 17 covers dates properly.
:::

## Worked example: a tiny journal app

Enough pieces — build something that survives being closed. This app appends entries, saves them
as JSON, and reads them back on startup.

```python
# journal.py
import json
from pathlib import Path

JOURNAL = Path(__file__).parent / "journal.json"


def load_entries():
    if not JOURNAL.exists():
        return []
    return json.loads(JOURNAL.read_text(encoding="utf-8"))


def save_entries(entries):
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def add_entry(entries, title, body):
    entries.append({"title": title, "body": body})


entries = load_entries()
print(f"{len(entries)} entries loaded.")
add_entry(entries, "First entry", "Learned pathlib today.")
save_entries(entries)
print(f"{len(entries)} entries saved to {JOURNAL}")
```

Run it twice and the second run reports one entry already loaded. That is persistence: state that
outlives the process. Swap `add_entry` for real `input()` calls and you have something you might
actually use.

## Atomic writes: never leave a half-written file

`write_text()` truncates first, then writes. If the process is killed midway — power cut, crash,
`Ctrl-C` — your journal is an empty or malformed file, and the data it replaced is gone. The fix is
to write a complete temporary file and then swap it into place, because replacing a file is a
single atomic operation at the filesystem level.

```python
import json
import os
import tempfile
from pathlib import Path


def save_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)      # atomic on every modern OS
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
```

Readers either see the complete old file or the complete new one — never a partially written one.
Use this for anything you cannot afford to lose: saved games in Chapter 33, user data in Chapter 30,
long-running exports.

:::pitfall Relative paths resolve against the working directory, not the script
`"data/config.json"` means "relative to wherever the terminal happened to be when you ran
`python3`", **not** "next to my script". Run the same program from a different folder and it
either crashes with `FileNotFoundError` or, far worse, silently creates a second stray file
somewhere else.

```python
# fragile
with open("config.json") as f: ...

# robust — anchored to the file's own folder
from pathlib import Path
BASE = Path(__file__).parent
with open(BASE / "config.json", encoding="utf-8") as f: ...
```

`__file__` is the path of the current module, so `Path(__file__).parent` is always the folder the
code lives in, regardless of where it was launched from. Anchor project data there. Use
`Path.cwd()` only when you deliberately mean "wherever the user is standing" — such as a CLI
operating on the user's current directory, which is exactly what Chapter 23 does.
:::

:::scenario The report ran fine on your laptop and found nothing on the server
A scheduled job reads `reports/daily.csv`, processes it, and emails a summary. Locally it works.
On the server, cron runs it from `/` and the job reports "0 rows processed" every single night for
a week before anyone notices. No error, no alert.
:::

:::solution Anchor paths, then fail loudly on missing files
Two mistakes stacked. First, the relative path resolved against `/` and found nothing. Second, the
code treated "no file" as "no rows" instead of an error:

```python
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = BASE / "reports" / "daily.csv"

if not source.is_file():
    raise SystemExit(f"expected input file not found: {source}")

rows = list(csv.DictReader(source.open(newline="", encoding="utf-8")))
if not rows:
    raise SystemExit(f"{source} exists but is empty — refusing to send an empty report")
```

Note `.resolve()` — it turns the path into an absolute one, which makes log messages unambiguous
when someone reads them six months later. The deeper habit: **validate inputs at the boundary and
fail fast**. A job that crashes loudly at 02:00 gets fixed on day one; a job that silently succeeds
with zero rows costs a week of missing data. Chapter 9 turns this instinct into proper exception
handling, and Chapter 11 covers logging these failures so they reach a human.
:::

## Key takeaways

- `Path` from `pathlib` represents paths as objects; use `/` to join segments and
  `name/stem/suffix/parent` to take them apart.
- `write_text()` / `read_text()` handle whole small files; always pass `encoding="utf-8"`.
- Always open files with `with` so they close even when an exception is raised.
- `"r"` reads, `"w"` truncates, `"a"` appends, `"x"` creates exclusively, `"b"` means binary.
- Iterate a file object to process large files line by line instead of `read()`.
- `csv.DictWriter` / `csv.DictReader` map rows to dicts; always pass `newline=""` when writing and
  convert strings to numbers yourself.
- `json.dump`/`load` work with files, `dumps`/`loads` with strings; `indent=2` makes output
  readable, and only JSON-native types can be serialised.
- Write to a temp file and `os.replace()` it for atomic saves; anchor data paths with
  `Path(__file__).parent`.

## Practice

- [ ] Write `explore.py`: create a folder `playground/sub`, write `"hello"` into
      `playground/sub/a.txt`, then print whether the path exists, whether it is a file, and its
      `name`, `stem`, and `suffix`.
- [ ] Write `linecount.py`: count the lines in any text file given as a filename, reading it line
      by line with `with`, and print the count.
- [ ] Write `grades.csv` by hand (three students, columns `name`, `grade`), then write
      `grades.py` that reads it with `csv.DictReader` and prints each name with their grade
      converted to an `int`, plus the class average.
- [ ] Write `settings.py`: save a dict of settings to `settings.json` with `indent=2`, read it
      back with `json.load`, change one value, and save it again.
- [ ] Extend `journal.py` from this chapter so it asks the user for a title and body with
      `input()`, appends the entry, saves with the atomic `save_json_atomic` function, and then
      prints every stored entry with a number.
- [ ] Write `backup.py`: copy every `.txt` file found recursively under a source folder into a
      destination folder, creating subdirectories with `mkdir(parents=True, exist_ok=True)`, and
      printing a list of what it copied. Use `Path.rglob` and read/write text; skip a file if the
      destination already exists.

## Solutions

:::solution Exercise 1
```python
# explore.py
from pathlib import Path

folder = Path("playground") / "sub"
folder.mkdir(parents=True, exist_ok=True)
file = folder / "a.txt"
file.write_text("hello", encoding="utf-8")

print(file.exists(), file.is_file())
print(file.name, file.stem, file.suffix, sep=" | ")
```
```text
True True
a.txt | a | .txt
```
`mkdir(parents=True, exist_ok=True)` creates both `playground` and `sub` in one call and does not
complain if they already exist. `stem` and `suffix` are how you rename a file while keeping its
folder — `file.with_suffix(".md")`.
:::

:::solution Exercise 2
```python
# linecount.py
from pathlib import Path
import sys

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__)
count = 0
with path.open(encoding="utf-8") as f:
    for _ in f:
        count += 1
print(f"{path}: {count} lines")
```
Iterating the file object yields one line at a time, so this works on files far larger than
memory. `sys.argv` is the list of command-line arguments — Chapter 20 builds real CLI tools on it.
:::

:::solution Exercise 3
```python
# grades.py
import csv
from pathlib import Path

path = Path(__file__).parent / "grades.csv"
with path.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

total = 0
for row in rows:
    grade = int(row["grade"])
    total += grade
    print(f"{row['name']}: {grade}")
print(f"average: {total / len(rows):.1f}")
```
Every value from CSV is a string, so `int(row["grade"])` is mandatory before doing arithmetic.
Anchoring the path to `Path(__file__).parent` means the script works no matter where you run it
from.
:::

:::solution Exercise 4
```python
# settings.py
import json
from pathlib import Path

path = Path(__file__).parent / "settings.json"
settings = {"theme": "dark", "font_size": 14, "recent_files": ["a.py", "b.py"]}

path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
loaded = json.loads(path.read_text(encoding="utf-8"))
loaded["font_size"] = 16
path.write_text(json.dumps(loaded, indent=2), encoding="utf-8")
print(json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=2))
```
The round-trip through text is what makes the file durable: `dumps` produces a string, `loads`
parses one. Note the list survived intact — lists and dicts nest cleanly in JSON.
:::

:::solution Exercise 5
```python
# journal.py — interactive version
import json
import os
import tempfile
from pathlib import Path

JOURNAL = Path(__file__).parent / "journal.json"


def save_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


entries = json.loads(JOURNAL.read_text(encoding="utf-8")) if JOURNAL.exists() else []
entries.append({"title": input("Title: "), "body": input("Body: ")})
save_json_atomic(JOURNAL, entries)

for i, entry in enumerate(entries, start=1):
    print(f"{i}. {entry['title']} — {entry['body']}")
```
The conditional expression loads existing entries or starts from an empty list. Because the save
is atomic, killing the program halfway leaves the previous journal intact rather than a truncated
JSON file that fails to parse next run.
:::

:::solution Exercise 6
```python
# backup.py
from pathlib import Path

base = Path(__file__).parent
source = base / "notes"
dest = base / "notes_backup"
dest.mkdir(parents=True, exist_ok=True)

copied = []
for src in sorted(source.rglob("*.txt")):
    target = dest / src.relative_to(source)
    if target.exists():
        continue
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    copied.append(target)

print(f"copied {len(copied)} files")
for path in copied:
    print(" -", path)
```
Anchoring both folders to `Path(__file__).parent` means the script behaves the same wherever it is
launched from. `src.relative_to(source)` turns an absolute nested path back into a relative one so
the folder structure is mirrored under the destination. `rglob("*.txt")` does the recursive search, and
`mkdir(parents=True, exist_ok=True)` inside the loop creates each nested folder as it is needed.
:::

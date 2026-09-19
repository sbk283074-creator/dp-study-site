# Chapter 23 (TaskForge) — verification report

Verified by building the project exactly as printed and running it.

* Build: `/Users/lucas.ma/Downloads/PYTHON/verify/taskforge/` (files copied verbatim from the chapter;
  only the two chapter-sanctioned additions below — `reopen` and `--week` — were added so the
  documented commands could be exercised).
* Env: Python 3.13.12, SQLAlchemy 2.0.52, typer 0.27.2, click 8.5.0, rich 15.0.0, pytest 9.1.1,
  ruff 0.16.6, mypy 2.3.1.
* Result: **the app does not run as printed** (bug 1 kills every command). After fixing bug 1 it runs
  end to end, and all 15 tests pass.
* Line numbers below are lines in `chapters/23-project-taskforge.md`.

---

### 1. `_v1_initial` creates the tables on a *second* connection — every command dies on a fresh database

**Where:** line 1208, `migrations.py`

```python
def _v1_initial(conn: Connection) -> None:
    from taskforge.models import Base

    Base.metadata.create_all(conn.engine)   # <-- conn.engine, not conn
```

**What breaks:** the very first command against a new database. `ensure_schema` holds an open write
transaction on `conn` (`CREATE TABLE schema_version` + `INSERT`), and `conn.engine` then opens a
*second* SQLite connection which cannot write while the first holds the reserved lock:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
  File ".../taskforge/migrations.py", line 33, in ensure_schema
  File ".../taskforge/db.py", line 33, in init_db
  File ".../taskforge/cli.py", line 56, in main
```

Reproduced with `taskforge project add work --description "Day job"` on an empty database.

**Fix:**

```python
def _v1_initial(conn: Connection) -> None:
    from taskforge.models import Base

    Base.metadata.create_all(conn)
```

---

### 2. The documented `report --week` does not exist

**Where:** line 28 (figure caption: "`taskforge report --week` collapses a week of activity…") vs the
command at lines 1030–1043, which only defines `--days`.

**What breaks:**

```
$ taskforge report --week
Usage: python -m taskforge report [OPTIONS]
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ No such option: --week                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

(exit code 2). Either the figure or the code is wrong; pick one and make both agree.

**Fix (as applied in the verified build):**

```python
@app.command()
def report(
    ctx: typer.Context,
    days: int = typer.Option(7, "--days", min=1, max=90),
    week: bool = typer.Option(False, "--week", help="Shorthand for --days 7."),
) -> None:
    """Summarise the last N days."""
    if week:
        days = 7
    ...
```

---

### 3. `reopen` is promised in the brief and implemented in the service, but never exposed in the CLI

**Where:** brief line 38 ("Create, list, complete, **reopen**, and delete tasks"), service
`reopen_task` at line 655; the CLI (Milestone 6, lines 931–1121) has no `reopen` command. The command
only appears later, inside the scenario box at line 1484.

**What breaks:**

```
$ taskforge reopen 1
╭─ Error ──────────────────────────────────────────────────────────────────────╮
│ No such command 'reopen'.                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

A reader who builds only Milestones 1–6 gets a service method with no way to call it.

**Fix:** move the command from line 1484 into the Milestone 6 CLI (it works verbatim):

```python
@app.command()
def reopen(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Undo a completion."""
    with task_service(ctx) as service:
        task = service.reopen_task(task_id)
    console.print(f"[cyan]reopened[/cyan] #{task.id} {task.title}")
```

---

### 4. A bad `--due` value escapes as a raw traceback instead of an `error:` line

**Where:** line 942 `due_at = parse_due(due) if due else None`, and `dates.py` lines 849 / 854–856
which raise plain `ValueError`.

**What breaks:** the chapter's own rule (lines 1176–1180: print user-facing errors to stderr, results
to stdout, non-zero exit) is violated:

```
$ taskforge add "Bad due date" --due "next tuesday"
...full rich traceback...
ValueError: cannot parse due date 'next tuesday'; use today, tomorrow, +3d or YYYY-MM-DD
```

exit code 1, traceback on stderr. Same for `+3w` and for `-1d` (a past relative date is not supported
at all: `text.startswith("+")` is the only relative form).

**Fix:** translate it at the CLI boundary:

```python
    due_at = None
    if due:
        try:
            due_at = parse_due(due)
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
```

(`typer.BadParameter` prints `Error: …` + usage and exits 2.)

---

### 5. `import` silently drops `archived` and `created_at`

**Where:** `import_data`, lines 764–787. `export_data` writes `"archived"` (line 750) and
`"created_at"` (line 740); `import_data` reads neither.

**What breaks:** a round trip is lossy. Exported an archived `home` project, imported into a fresh
database:

```
$ taskforge import demo-export.json
imported 2 project(s), 3 task(s), 0 skipped
$ taskforge project list --all
│ home │    2 │          │      <-- archived flag lost
```

and every imported task gets `created_at = now`, so `report --week` afterwards reports *all* imported
tasks as "Created" in the last 7 days, no matter how old they are.

**Fix:**

```python
            if project is None:
                project = self.repo.add_project(name, raw_project.get("description", ""))
                project.archived = bool(raw_project.get("archived", False))
                projects += 1
...
                task = self.repo.add_task(
                    project,
                    title,
                    notes=raw_task.get("notes", ""),
                    priority=Priority(raw_task.get("priority", Priority.MEDIUM.value)),
                    due_at=_parse_iso(raw_task.get("due_at")),
                    created_at=_parse_iso(raw_task.get("created_at")) or utcnow(),
                )
```

which also needs `created_at: datetime | None = None` on `TaskRepository.add_task` (line 437):

```python
        task = Task(
            project=project, title=title, notes=notes, priority=priority,
            due_at=due_at, created_at=created_at or utcnow(),
        )
```

---

### 6. The tag filter is case-sensitive, so `--tag Work` returns nothing

**Where:** `repository.py` line 474 `stmt = stmt.join(Task.tags).where(Tag.name == tag)`; the value is
passed through untouched by `TaskService.find` (lines 683 / 705). Writes *are* normalised
(lines 642, 671, and the scenario fix at 1523–1530: `.strip().lower()`).

**What breaks:** exactly the silent-wrong-subset problem the chapter's own tag scenario complains
about:

```
$ taskforge list --tag Q3
                 0 task(s)
$ taskforge list --tag q3
                 1 task(s)
```

**Fix:** normalise on read too (cheapest: in the repository, next to the normalised write):

```python
        if tag is not None:
            normalised = tag.strip().lower()
            stmt = stmt.join(Task.tags).where(Tag.name == normalised)
```

---

### 7. `_v2_merge_duplicate_tags` keeps the old spelling, so the duplicates come straight back

**Where:** lines 1538–1554 (scenario solution). The surviving row is whatever spelling was inserted
first; the merge never lower-cases it, while every new write *is* lower-cased.

**What breaks:** after merging `Work` / `work` / `WORK` the table holds `(1, 'Work')`. The next
`repo.get_or_create_tag("work")` inserts a new row, so the tags table ends up as
`[(1, 'Work'), (2, 'work')]` — two tags again, and `list --tag work` matches only the tasks written
after the migration. Verified by running the snippet against a real database.

**Fix:** rename the survivor to the normalised key:

```python
    for tag_id, name in rows:
        key = name.strip().lower()
        canonical_id = canonical.setdefault(key, tag_id)
        conn.execute(
            text("UPDATE tags SET name = :norm WHERE id = :keep"),
            {"norm": key, "keep": canonical_id},
        )
        if canonical_id == tag_id:
            continue
        ...
```

---

### 8. `mypy src` (strict, as configured) fails with 6 errors

**Where:** `db.py` lines 319, 324, 330, 334; `services.py` lines 730, 756.

```
src/taskforge/db.py:16: error: Function is missing a return type annotation   [no-untyped-def]
src/taskforge/db.py:21: error: Function is missing a type annotation          [no-untyped-def]
src/taskforge/db.py:27: error: Function is missing a type annotation for one or more parameters [no-untyped-def]
src/taskforge/db.py:31: error: Function is missing a type annotation for one or more parameters [no-untyped-def]
src/taskforge/services.py:201: error: Missing type arguments for generic type "dict" [type-arg]
src/taskforge/services.py:227: error: Missing type arguments for generic type "dict" [type-arg]
```

**Fix:**

```python
# db.py
def create_engine_from_settings(settings: Settings) -> Engine: ...
    def _enable_foreign_keys(dbapi_connection: sqlite3.Connection, _record: Any) -> None: ...
def make_session_factory(engine: Engine) -> sessionmaker[Session]: ...
def init_db(engine: Engine) -> None: ...

# services.py
    def export_data(self) -> dict[str, object]: ...
    def import_data(self, payload: dict[str, object], *, merge: bool = True) -> ImportResult: ...
```

---

### 9. `ruff check .` fails with 18 errors and `ruff format --check .` would reformat 4 files

The milestone checklist (line 1630) claims `ruff check . && ruff format --check .` is clean. With the
chapter's own `[tool.ruff]` config (line-length 100, `select = ["E","F","I","UP","B","SIM"]`) it is
not.

**Where / what:**

* `E501` line too long — `cli.py:1003` (`def done(...)` = 102 chars) and `cli.py:1047`
  (`def export(...)` = 105 chars).
* `F401` unused imports — `services.py:537` (`Tag`), `tests/test_repository.py:1298` (`Status`),
  `tests/test_services.py:1340` (`timedelta`).
* `I001` unsorted imports — `db.py:311-312` (two separate `from sqlalchemy import …` lines),
  `migrations.py:1202` (`Engine, Connection, text` → `Connection, Engine, text`),
  `services.py:535` (`datetime, timedelta, time` → `datetime, time, timedelta`).
* `B008` function call in argument default — 7 hits, one for every `typer.Option(...)` /
  `typer.Argument(...)` default in `cli.py`. This is a well-known false positive for Typer.
* `UP017` — `models.py:171` `timezone.utc` → `datetime.UTC`.
* `UP042` — `models.py:178` and `:183`, `class Status(str, enum.Enum)` → `enum.StrEnum` on 3.12+.
* `ruff format --check` would reformat 4 files: `models.py:216` (the `relationship(...)` call),
  `repository.py:446` (`task = Task(...)`), `services.py:638` (`self.repo.add_task(...)`),
  `cli.py:908` (the `--version` option) — all because the trailing comma keeps a call split that
  fits on one line.

**Fix:** apply the import/line fixes, and either add to `pyproject.toml`

```toml
[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["typer.Argument", "typer.Option"]
```

or drop `B` / add a per-file ignore for `cli.py`. Then run `ruff format .` once and re-print the four
affected snippets in the chapter.

---

### 10. Two different migrations are both numbered `_v2`

**Where:** lines 1230–1235 (`_v2_add_recurring`, `MIGRATIONS = [_v1_initial, _v2_add_recurring]`) and
lines 1537–1557 (`_v2_merge_duplicate_tags`, `MIGRATIONS = [_v1_initial, _v2_merge_duplicate_tags]`).

**What breaks:** nothing at runtime (they are separate examples), but a reader who follows the
chapter in order appends two distinct "version 2" steps and has to invent the renumbering the chapter
never mentions — while the file's own docstring (lines 1194–1195) says "Never edit a released
migration; add a new one."

**Fix:** call the second one `_v3_merge_duplicate_tags` /
`MIGRATIONS = [_v1_initial, _v2_add_recurring, _v3_merge_duplicate_tags]`, and say explicitly that the
reader picks whichever v2 their own schema needs.

---

### 11. `parse_due` mixes local dates with UTC "now", so `--due today` can be overdue immediately

**Where:** `dates.py` lines 836–850 — the docstring says "Returns midnight **UTC**" but
`today = today or date.today()` uses the *local* date; `is_overdue` (line 579) and `find`
(line 699) compare against `utcnow().date()`, i.e. the *UTC* date.

**What breaks:** for any user whose local date differs from the UTC date (UTC−11 … UTC−5 in the
morning, UTC+10 … +14 in the evening):

```
$ TZ=Pacific/Midway taskforge add "Due today" --due today
added #1 Due today in inbox
$ TZ=Pacific/Midway taskforge list --overdue
│  1 │ Due today │ inbox │ medium │ 2026-09-07 │      <-- due "today", already overdue
```

(UTC now was `2026-09-08 02:29`; the local date was `2026-09-07`.)

**Fix:** make the two sides use the same clock. Either store UTC and parse against UTC,

```python
def parse_due(value: str, *, today: date | None = None) -> datetime:
    text = value.strip().lower()
    today = today or datetime.now(timezone.utc).date()   # UTC, matching utcnow()
```

and say so in the docstring, or keep local dates and compare with `date.today()` in `is_overdue`/`find`.

---

### 12. Notes can be written but never read; tags can be added but never removed

**Where:** `models.py:242` / `cli.py:939` (`--notes`), and the command list at lines 931–1121.

**What breaks:** nothing crashes, but the brief (line 39) sells notes and tags as first-class. There is
no `untag` command (`taskforge untag 3 shopping` → `No such command 'untag'. Did you mean 'tag'?`), no
`note`/`edit` command, and `list` has no Notes column — the only way to see a note is
`list --search <word>`.

**Fix:** add the missing pair, e.g. `services.untag_task(task_id, *names)` plus

```python
@app.command()
def untag(ctx: typer.Context, task_id: int = typer.Argument(...),
          names: list[str] = typer.Argument(...)) -> None:
    """Remove tags from a task."""
```

and either a `show <id>` command or a Notes column in `list`.

---

### 13. "17 passed in 0.42s" does not match the tests in the chapter

**Where:** line 1466–1468.

**What breaks:** the chapter defines 14 tests (4 in `test_repository.py`, 8 in `test_services.py`,
2 in `test_cli.py`); with the scenario's `test_reopen_clears_completed_at` (line 1494) it is 15. The
verified run is:

```
15 passed in 0.50s
```

**Fix:** print the real number, or add the two tests that are missing.

---

## Areas that are clean (verified as printed)

* **`models.py`** — runs unmodified; enums, `PRIORITY_RANK`, the naive-UTC `utcnow()`, the `task_tag`
  association table and the `due_at` index all behave. (Only the two `UP` lint nits above. Note for
  the curious: SQLAlchemy's `Enum` persists the enum **name**, so the column contains `'HIGH'`, not
  `'high'` — harmless because every read/write goes through the enum, and the JSON export/import uses
  `.value`.)
* **`config.py`** — `TASKFORGE_DB` / `TASKFORGE_LOG`, `~` expansion and parent-directory creation all
  work.
* **`logging_setup.py`** — only the `taskforge` logger is touched; `--verbose` adds the stream handler.
* **`db.py`** — `session_scope`, `expire_on_commit=False` and the `PRAGMA foreign_keys=ON` listener are
  correct; deleting a project cascades through `tasks` **and** `task_tag` (verified: rows go to `[]`).
  `future=True` is a no-op on 2.0 but not an error.
* **`dates.py`** — `today`, `tomorrow`, `+3d` and `YYYY-MM-DD` all parse correctly (only the UTC/local
  mismatch of bug 11 and the uncaught `ValueError` of bug 4).
* **`repository.py`** — all six filters (`project`, `status`, `priority`, `tag`, `search`,
  `due_before`), `ilike` search, `nulls_last()` ordering, `created_since` / `completed_since` and
  `get_or_create_tag` all work on SQLAlchemy 2.0.52. `is_not(None)` is legacy but fine.
* **`services.py`** — every rule behaves: project auto-create, archived-project freeze, duplicate
  project rejection, blank/over-long title rejection, complete/reopen, priority sort, weekly report,
  export/import (bar bug 5).
* **`migrations.py`** apart from bug 1: `from sqlalchemy import Engine, Connection, text` (line 1202)
  *does* import cleanly on 2.0.52, and the versioned `MIGRATIONS` loop is correct — a second run
  skips v1. The tag-merge snippet runs (bar bug 7).
* **Tests** — all pass once the project is assembled: `15 passed`. With click ≥ 8.2 `result.output`
  mixes stderr, so `test_unknown_task_exits_non_zero` passes as written; `taskforge done 999` really
  does print `error: no task with id #999` and exit 1.
* **CLI surface** — `--help` works for the app and for every subcommand (`add`, `list`, `done`, `rm`,
  `tag`, `reopen`, `report`, `export`, `import`, `project add|list|archive|rm`), `--version` works,
  `no_args_is_help` works, `project rm` prompts without `--force` and deletes with it, and the
  `[project.scripts]` entry point `taskforge` works from an editable install.

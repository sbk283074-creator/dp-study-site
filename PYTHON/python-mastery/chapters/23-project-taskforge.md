---
chapter: 23
part: 3
title: "PROJECT: TaskForge — A Real CLI Application"
summary: Build, test, and package a complete command-line task manager with SQLAlchemy, Typer, pytest, and a layered architecture you can reuse on any project.
minutes: 120
tags: [project, sqlalchemy, typer, pytest, architecture, cli, packaging]
---

Everything before this chapter was practice. This is the first program in the book that you could
hand to another person and have them use it: a task manager that lives in your terminal, keeps
its data in SQLite, and survives being closed. It is deliberately small enough to finish and
deliberately structured like a real application — separate layers for storage, rules, and
interface — because the structure is the part that transfers. Finish this and Chapter 30's web
app is mostly a new front end on the same skeleton.

Work through the milestones in order. Each one ends with something you can run.

## What you are building

A command-line tool has no windows, so its "screens" are its output. This is what using TaskForge
feels like once Milestone 5 is done: `taskforge project add` creates the project, `taskforge add`
files the work, and `taskforge list` shows it.

![`taskforge project add`, then `taskforge add` with a priority, a due date and two tags, then `taskforge list`. Note the — where a task has no due date: real data is always missing something. `taskforge list --overdue` narrows the same table to what is already late.](figures/taskforge-list.png)

And the weekly report from Milestone 6, which is the feature that makes the tool worth keeping.
`taskforge export` and `taskforge import` move that same data to another machine:

![`taskforge report --week` collapses a week of activity into four numbers and two breakdowns.](figures/taskforge-report.png)

Keep these in view as you build. Every milestone should move you towards output this calm. Boring,
predictable output is the goal — it means the tool has stopped surprising you and started working.

## The brief

TaskForge is a personal task manager for the command line:

- Create, list, archive, and delete **projects** ("work", "home", "renovation").
- Create, list, complete, reopen, and delete **tasks** inside a project.
- Give a task a **priority** (low, medium, high, urgent), a **due date**, free-text **notes**, and
  any number of **tags**.
- Filter and search: by project, status, priority, tag, free text, or "overdue".
- Print a **weekly report**: what you created, what you finished, what is late.
- **Export** everything to JSON and **import** it again on another machine.

Non-goals: no web UI (that is Chapter 30), no sync, no reminders, no multi-user accounts. Write
those down somewhere. Scope creep kills more side projects than bugs do.

## Milestone 1 — Project layout

```text
taskforge/
├── pyproject.toml
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── src/taskforge/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py            # Typer commands: parse args, print results
│   ├── config.py         # settings from environment variables
│   ├── db.py             # engine, session factory, transaction scope
│   ├── logging_setup.py  # logging configuration
│   ├── migrations.py     # ordered schema migrations
│   ├── models.py         # SQLAlchemy tables and enums
│   ├── repository.py     # every SQL statement in the app
│   ├── services.py       # business rules
│   └── dates.py          # due-date parsing
└── tests/
    ├── conftest.py
    ├── test_repository.py
    ├── test_services.py
    └── test_cli.py
```

Read that tree as a dependency arrow pointing downward. `cli` knows about `services`.
`services` knows about `repository` and `models`. `repository` knows about `models` and nothing
else. Nothing lower ever imports something higher. That single rule is what lets you test the
rules without a CLI and swap SQLite for Postgres without touching a rule.

`pyproject.toml` — the whole project's configuration in one file, as of Chapter 22:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "taskforge"
version = "0.1.0"
description = "A personal task manager for the command line"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = [
    "sqlalchemy>=2.0",
    "typer>=0.15",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.8",
    "mypy>=1.14",
]

[project.scripts]
taskforge = "taskforge.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/taskforge"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["typer.Argument", "typer.Option"]

[tool.mypy]
python_version = "3.12"
strict = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
```

The bugbear setting exists because `B` includes `B008`, "do not perform function calls in argument
defaults", and every `typer.Option(...)` default trips it. That is a known false positive: Typer is
built around reading those calls out of the signature, so listing them as immutable calls silences
the rule without weakening it anywhere else.

Set up the environment:

```bash
cd taskforge
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

The `-e` installs in **editable** mode: Python imports `taskforge` from `src/` directly, so every
save takes effect without reinstalling, and `taskforge` appears on your PATH.

## Milestone 2 — The data model

Four tables: `projects`, `tasks`, `tags`, and a `task_tag` association table for the
many-to-many between tasks and tags. One task belongs to exactly one project; one task can carry
many tags and one tag can sit on many tasks.

```python
# src/taskforge/models.py
"""Database models for TaskForge.

All timestamps are stored as *naive* UTC datetimes. SQLite has no time zone
type, so an "aware" column buys nothing and costs you "can't compare
offset-naive and offset-aware" errors. Store UTC; convert at the edges only.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (SQLite-safe)."""
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Declarative base shared by every TaskForge model."""


class Status(enum.StrEnum):
    TODO = "todo"
    DONE = "done"


class Priority(enum.StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Lower sorts first: urgent before low. The database stores priority as text,
# so ORDER BY priority would give you high, low, medium, urgent.
PRIORITY_RANK: dict[Priority, int] = {
    Priority.URGENT: 0,
    Priority.HIGH: 1,
    Priority.MEDIUM: 2,
    Priority.LOW: 3,
}

task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    archived: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    tasks: Mapped[list[Task]] = relationship(back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, archived={self.archived!r})"


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)

    tasks: Mapped[list[Task]] = relationship(secondary=task_tag, back_populates="tags")

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (Index("ix_tasks_due_at", "due_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.TODO)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    project: Mapped[Project] = relationship(back_populates="tasks")
    tags: Mapped[list[Tag]] = relationship(secondary=task_tag, back_populates="tasks")

    @property
    def is_done(self) -> bool:
        return self.status is Status.DONE

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r}, status={self.status.value!r})"
```

Three decisions worth defending:

- **Enums for status and priority.** The column can only hold a value you defined. Compare
  `task.status is Status.DONE` and you never typo a string.
- **Timestamps are defaults, not manual assignments.** `default=utcnow` means the model is
  correct no matter which layer creates the row.
- **`created_at` plus `completed_at`.** "Created" and "finished" are different questions and the
  weekly report asks both.

## Milestone 3 — Plumbing: config, database, logging

```python
# src/taskforge/config.py
"""Settings read from the environment, with sane defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOME = Path.home() / ".taskforge"


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    log_path: Path

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if env is None else env)
        url = env.get("TASKFORGE_DB") or f"sqlite:///{DEFAULT_HOME / 'taskforge.db'}"
        log_path = Path(env.get("TASKFORGE_LOG") or DEFAULT_HOME / "taskforge.log").expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if url.startswith("sqlite"):
            db_file = Path(url.split("///")[-1]).expanduser()
            db_file.parent.mkdir(parents=True, exist_ok=True)
        return cls(database_url=url, log_path=log_path)
```

```python
# src/taskforge/db.py
"""Engine, session factory, and the one place transactions are committed."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from taskforge.config import Settings
from taskforge.migrations import ensure_schema


def create_engine_from_settings(settings: Settings) -> Engine:
    engine = create_engine(settings.database_url, future=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(  # pragma: no cover
            dbapi_connection: sqlite3.Connection, _record: Any
        ) -> None:
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def init_db(engine: Engine) -> None:
    """Bring the database up to the current schema version."""
    ensure_schema(engine)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Commit on success, roll back on any exception, always close."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

`session_scope` is the whole transaction policy of the application, in nine lines. Callers cannot
forget to commit and cannot leave a half-applied change behind. `expire_on_commit=False` matters
too: without it, every attribute access after a commit triggers a fresh database query, and after
the session closes you get `DetachedInstanceError`. We print objects after the session closes, so
we keep them loaded.

```python
# src/taskforge/logging_setup.py
"""Logging configuration: quiet by default, chatty with --verbose."""

from __future__ import annotations

import logging
from pathlib import Path

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(log_path: Path, *, verbose: bool = False) -> None:
    logger = logging.getLogger("taskforge")
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    logger.propagate = False
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(file_handler)

    if verbose:
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(stream)
```

Configure only the `taskforge` logger, never the root logger. Grabbing the root logger hijacks
output from SQLAlchemy, Typer, and anything else the user has opinions about.

## Milestone 4 — The repository layer

Every SQL statement in TaskForge lives in this one class. Not "most" — all.

```python
# src/taskforge/repository.py
"""All SQL in TaskForge. Nothing here makes policy decisions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskforge.models import Priority, Project, Status, Tag, Task, utcnow


class TaskRepository:
    """Owns every query. Knows SQL; knows nothing about business rules."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ---------- projects ----------

    def add_project(self, name: str, description: str = "") -> Project:
        project = Project(name=name, description=description)
        self.session.add(project)
        self.session.flush()  # assign project.id without committing
        return project

    def get_project(self, name: str) -> Project | None:
        return self.session.scalar(select(Project).where(Project.name == name))

    def list_projects(self, *, include_archived: bool = False) -> list[Project]:
        stmt = select(Project).order_by(Project.name)
        if not include_archived:
            stmt = stmt.where(Project.archived.is_(False))
        return list(self.session.scalars(stmt))

    def delete_project(self, project: Project) -> None:
        self.session.delete(project)
        self.session.flush()

    # ---------- tasks ----------

    def add_task(
        self,
        project: Project,
        title: str,
        *,
        notes: str = "",
        priority: Priority = Priority.MEDIUM,
        due_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> Task:
        task = Task(
            project=project,
            title=title,
            notes=notes,
            priority=priority,
            due_at=due_at,
            created_at=created_at or utcnow(),
        )
        self.session.add(task)
        self.session.flush()
        return task

    def get_task(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def list_tasks(
        self,
        *,
        project: Project | None = None,
        status: Status | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search: str | None = None,
        due_before: datetime | None = None,
    ) -> list[Task]:
        stmt = select(Task)
        if project is not None:
            stmt = stmt.where(Task.project_id == project.id)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if tag is not None:
            normalised = tag.strip().lower()
            stmt = stmt.join(Task.tags).where(Tag.name == normalised)
        if search:
            pattern = f"%{search.lower()}%"
            stmt = stmt.where(Task.title.ilike(pattern) | Task.notes.ilike(pattern))
        if due_before is not None:
            stmt = stmt.where(Task.due_at.is_not(None), Task.due_at < due_before)
        stmt = stmt.order_by(Task.due_at.nulls_last(), Task.id)
        return list(self.session.scalars(stmt))

    def created_since(self, start: datetime) -> list[Task]:
        return list(self.session.scalars(select(Task).where(Task.created_at >= start)))

    def completed_since(self, start: datetime) -> list[Task]:
        return list(
            self.session.scalars(
                select(Task).where(Task.completed_at.is_not(None), Task.completed_at >= start)
            )
        )

    def delete_task(self, task: Task) -> None:
        self.session.delete(task)
        self.session.flush()

    # ---------- tags ----------

    def get_or_create_tag(self, name: str) -> Tag:
        tag = self.session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            self.session.add(tag)
            self.session.flush()
        return tag

    def list_tags(self) -> list[Tag]:
        return list(self.session.scalars(select(Tag).order_by(Tag.name)))
```

Notes on the details, because they are the point:

- `session.flush()` pushes the INSERT so the object gets its `id` (and so a uniqueness violation
  raises here, where you can handle it) without committing the transaction. Committing is
  `session_scope`'s job.
- Filters are keyword-only with `None` defaults, so callers pass only what they care about and the
  query stays readable.
- `list_tasks` deliberately does **not** sort by priority. Priority is stored as text, so SQL
  would order it alphabetically: high, low, medium, urgent. Correct ordering is a policy decision
  and lives one layer up.
- Tag names are stored normalised (stripped and lower-cased), so the tag filter normalises the
  value it is *given* too. Skip that and `list --tag Work` returns nothing while `list --tag work`
  returns everything: a silently wrong subset, which is the worst kind of wrong.
- The repository returns model objects and raises nothing of its own. It does not know that
  archived projects exist. That is somebody else's rule.

## Milestone 5 — The service layer

Rules live here: what is valid, what is allowed, what counts as overdue.

```python
# src/taskforge/services.py
"""Business rules. Talks to a TaskRepository, knows nothing about SQL or Typer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any

from taskforge.models import PRIORITY_RANK, Priority, Project, Status, Task, utcnow
from taskforge.repository import TaskRepository


class TaskForgeError(Exception):
    """Base class for every error TaskForge raises on purpose."""


class NotFoundError(TaskForgeError):
    pass


class ValidationError(TaskForgeError):
    pass


class ProjectArchivedError(TaskForgeError):
    pass


@dataclass(frozen=True, slots=True)
class WeeklyReport:
    start: datetime
    end: datetime
    created: int
    completed: int
    overdue: list[Task] = field(default_factory=list)
    by_priority: dict[Priority, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ImportResult:
    projects: int = 0
    tasks: int = 0
    skipped: int = 0


def is_overdue(task: Task, now: datetime | None = None) -> bool:
    """A task is overdue when its due date is before today and it is not done."""
    if task.status is Status.DONE or task.due_at is None:
        return False
    now = now or utcnow()
    return task.due_at.date() < now.date()


class TaskService:
    """Every rule in TaskForge, expressed over a repository."""

    MAX_TITLE = 200

    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    # ---------- projects ----------

    def create_project(self, name: str, description: str = "") -> Project:
        name = self._clean_name(name, "project name")
        if self.repo.get_project(name) is not None:
            raise ValidationError(f"project {name!r} already exists")
        return self.repo.add_project(name, description)

    def get_or_create_project(self, name: str, description: str = "") -> Project:
        name = self._clean_name(name, "project name")
        project = self.repo.get_project(name)
        if project is None:
            return self.repo.add_project(name, description)
        if project.archived:
            raise ProjectArchivedError(f"project {name!r} is archived and frozen")
        return project

    def list_projects(self, *, include_archived: bool = False) -> list[Project]:
        return self.repo.list_projects(include_archived=include_archived)

    def archive_project(self, name: str) -> Project:
        project = self._require_project(name)
        project.archived = True
        return project

    def delete_project(self, name: str) -> None:
        project = self._require_project(name)
        self.repo.delete_project(project)

    # ---------- tasks ----------

    def create_task(
        self,
        project_name: str,
        title: str,
        *,
        notes: str = "",
        priority: Priority = Priority.MEDIUM,
        due_at: datetime | None = None,
        tags: tuple[str, ...] | list[str] = (),
    ) -> Task:
        title = (title or "").strip()
        if not title:
            raise ValidationError("task title cannot be empty")
        if len(title) > self.MAX_TITLE:
            raise ValidationError(f"task title is limited to {self.MAX_TITLE} characters")

        project = self.get_or_create_project(project_name)
        task = self.repo.add_task(project, title, notes=notes, priority=priority, due_at=due_at)
        for name in tags:
            task.tags.append(self.repo.get_or_create_tag(name.strip().lower()))
        return task

    def get_task(self, task_id: int) -> Task:
        """Fetch one task by id; raises NotFoundError if it does not exist."""
        return self._require_task(task_id)

    def complete_task(self, task_id: int, *, at: datetime | None = None) -> Task:
        task = self._require_task(task_id)
        if task.project.archived:
            raise ProjectArchivedError(f"project {task.project.name!r} is archived")
        if task.status is Status.DONE:
            raise ValidationError(f"task #{task_id} is already done")
        task.status = Status.DONE
        task.completed_at = at or utcnow()
        return task

    def reopen_task(self, task_id: int) -> Task:
        task = self._require_task(task_id)
        if task.status is Status.TODO:
            raise ValidationError(f"task #{task_id} is not done")
        task.status = Status.TODO
        task.completed_at = None
        return task

    def delete_task(self, task_id: int) -> Task:
        task = self._require_task(task_id)
        self.repo.delete_task(task)
        return task

    def tag_task(self, task_id: int, *names: str) -> Task:
        task = self._require_task(task_id)
        for name in names:
            cleaned = name.strip().lower()
            if not cleaned:
                continue
            tag = self.repo.get_or_create_tag(cleaned)
            if tag not in task.tags:
                task.tags.append(tag)
        return task

    def untag_task(self, task_id: int, *names: str) -> Task:
        task = self._require_task(task_id)
        drop = {name.strip().lower() for name in names if name.strip()}
        task.tags = [tag for tag in task.tags if tag.name not in drop]
        return task

    def find(
        self,
        *,
        project_name: str | None = None,
        status: Status | None = None,
        priority: Priority | None = None,
        tag: str | None = None,
        search: str | None = None,
        overdue_only: bool = False,
        include_done: bool = False,
        now: datetime | None = None,
    ) -> list[Task]:
        now = now or utcnow()
        project = None
        if project_name is not None:
            project = self._require_project(project_name)

        # An explicit --status wins; otherwise hide done tasks unless asked.
        status_filter = status if status is not None else (None if include_done else Status.TODO)

        due_before = datetime.combine(now.date(), time.min) if overdue_only else None

        tasks = self.repo.list_tasks(
            project=project,
            status=status_filter,
            priority=priority,
            tag=tag,
            search=search,
            due_before=due_before,
        )
        tasks.sort(key=lambda t: (PRIORITY_RANK[t.priority], t.due_at or datetime.max, t.id))
        return tasks

    def weekly_report(self, days: int = 7, *, now: datetime | None = None) -> WeeklyReport:
        now = now or utcnow()
        start = now - timedelta(days=days)
        open_tasks = self.repo.list_tasks(status=Status.TODO)
        by_priority: dict[Priority, int] = {}
        for task in open_tasks:
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        return WeeklyReport(
            start=start,
            end=now,
            created=len(self.repo.created_since(start)),
            completed=len(self.repo.completed_since(start)),
            overdue=[t for t in open_tasks if is_overdue(t, now)],
            by_priority=by_priority,
        )

    # ---------- import / export ----------

    def export_data(self) -> dict[str, Any]:
        projects = []
        for project in self.repo.list_projects(include_archived=True):
            tasks = [
                {
                    "title": t.title,
                    "notes": t.notes,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "due_at": t.due_at.isoformat() if t.due_at else None,
                    "created_at": t.created_at.isoformat(),
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                    "tags": [tag.name for tag in t.tags],
                }
                for t in self.repo.list_tasks(project=project)
            ]
            projects.append(
                {
                    "name": project.name,
                    "description": project.description,
                    "archived": project.archived,
                    "tasks": tasks,
                }
            )
        return {"version": 1, "exported_at": utcnow().isoformat(), "projects": projects}

    def import_data(self, payload: dict[str, Any], *, merge: bool = True) -> ImportResult:
        if payload.get("version") != 1:
            raise ValidationError(f"unsupported export version: {payload.get('version')!r}")

        projects = tasks = skipped = 0
        for raw_project in payload.get("projects", []):
            name = self._clean_name(raw_project.get("name", ""), "project name")
            project = self.repo.get_project(name)
            if project is None:
                project = self.repo.add_project(name, raw_project.get("description", ""))
                project.archived = bool(raw_project.get("archived", False))
                projects += 1
            for raw_task in raw_project.get("tasks", []):
                title = (raw_task.get("title") or "").strip()
                if not title:
                    skipped += 1
                    continue
                if merge and any(t.title == title for t in project.tasks):
                    skipped += 1
                    continue
                task = self.repo.add_task(
                    project,
                    title,
                    notes=raw_task.get("notes", ""),
                    priority=Priority(raw_task.get("priority", Priority.MEDIUM.value)),
                    due_at=_parse_iso(raw_task.get("due_at")),
                    created_at=_parse_iso(raw_task.get("created_at")) or utcnow(),
                )
                if raw_task.get("status") == Status.DONE.value:
                    task.status = Status.DONE
                    task.completed_at = _parse_iso(raw_task.get("completed_at")) or utcnow()
                for tag_name in raw_task.get("tags", []):
                    task.tags.append(self.repo.get_or_create_tag(tag_name))
                tasks += 1
        return ImportResult(projects=projects, tasks=tasks, skipped=skipped)

    # ---------- internals ----------

    def _require_project(self, name: str) -> Project:
        project = self.repo.get_project(name)
        if project is None:
            raise NotFoundError(f"no project named {name!r}")
        return project

    def _require_task(self, task_id: int) -> Task:
        task = self.repo.get_task(task_id)
        if task is None:
            raise NotFoundError(f"no task with id #{task_id}")
        return task

    @staticmethod
    def _clean_name(value: str, label: str) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValidationError(f"{label} cannot be empty")
        return cleaned


def _parse_iso(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None
```

Look at what this class does *not* contain: no `select()`, no `print()`, no `typer`. Give it a
repository pointed at an in-memory SQLite database and every rule above is testable in
microseconds with no CLI and no filesystem policy. Give it a repository backed by Postgres and
nothing here changes. That is the payoff of the separation, and it is why the split is worth the
extra file.

The export/import round trip has to be lossless, which is why `import_data` restores `archived`
and `created_at` and not just the fields a human would notice. Drop `archived` and a frozen
project thaws on the other machine; drop `created_at` and every imported task is stamped "now",
so the next weekly report claims you created all two hundred of them this morning. When you add
a column to `export_data`, add it to `import_data` in the same commit.

## Milestone 6 — The CLI

The CLI parses arguments, calls one service method, and prints. Any `if` in here that is not
about presentation is a rule that escaped from the service layer.

```python
# src/taskforge/dates.py
"""Parse the due-date formats the CLI accepts."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta


def parse_due(value: str, *, today: date | None = None) -> datetime:
    """Accept 'today', 'tomorrow', '+3d', or YYYY-MM-DD.

    Returns midnight on the matching day, as naive UTC. Relative words are
    resolved against the *UTC* date, because that is the clock `utcnow()` and
    the overdue comparison use; `date.today()` is the local date and disagrees
    with them for several hours of every day.
    """
    text = value.strip().lower()
    today = today or datetime.now(UTC).date()

    if text == "today":
        return datetime.combine(today, time.min)
    if text == "tomorrow":
        return datetime.combine(today + timedelta(days=1), time.min)
    if text.startswith("+"):
        try:
            days = int(text[1:].removesuffix("d"))
        except ValueError:
            raise ValueError(f"cannot parse relative due date {value!r}") from None
        return datetime.combine(today + timedelta(days=days), time.min)
    try:
        return datetime.combine(date.fromisoformat(text), time.min)
    except ValueError:
        raise ValueError(
            f"cannot parse due date {value!r}; use today, tomorrow, +3d or YYYY-MM-DD"
        ) from None
```

```python
# src/taskforge/cli.py
"""Typer front end: parse arguments, call a service, print the result."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from taskforge import __version__
from taskforge.config import Settings
from taskforge.dates import parse_due
from taskforge.db import create_engine_from_settings, init_db, make_session_factory, session_scope
from taskforge.logging_setup import configure_logging
from taskforge.models import Priority, Status
from taskforge.repository import TaskRepository
from taskforge.services import TaskForgeError, TaskService, is_overdue

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="TaskForge - a task manager for your terminal.",
)
project_app = typer.Typer(no_args_is_help=True, help="Create and manage projects.")
app.add_typer(project_app, name="project")

console = Console(width=120)
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"taskforge {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Log debug detail to stderr and the log file."
    ),
    version: bool | None = typer.Option(
        None, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """TaskForge: projects, tasks, tags, due dates and reports."""
    settings = Settings.from_env()
    configure_logging(settings.log_path, verbose=verbose)
    engine = create_engine_from_settings(settings)
    init_db(engine)
    ctx.obj = {"session_factory": make_session_factory(engine), "settings": settings}


@contextmanager
def task_service(ctx: typer.Context) -> Iterator[TaskService]:
    """Open a transaction, hand over a service, and translate errors to exit codes."""
    with session_scope(ctx.obj["session_factory"]) as session:
        try:
            yield TaskService(TaskRepository(session))
        except TaskForgeError as exc:
            err_console.print(f"[bold red]error:[/bold red] {exc}")
            raise typer.Exit(code=1) from exc


@app.command()
def add(
    ctx: typer.Context,
    title: str = typer.Argument(..., help="What needs doing."),
    project: str = typer.Option("inbox", "--project", "-p", help="Project (created if new)."),
    priority: Priority = typer.Option(Priority.MEDIUM, "--priority", help="low|medium|high|urgent"),
    due: str | None = typer.Option(None, "--due", "-d", help="today, tomorrow, +3d or YYYY-MM-DD."),
    tag: list[str] | None = typer.Option(None, "--tag", "-t", help="Repeatable."),
    notes: str = typer.Option("", "--notes", "-n", help="Free-text detail."),
) -> None:
    """Create a task."""
    due_at = None
    if due:
        try:
            due_at = parse_due(due)
        except ValueError as exc:
            raise typer.BadParameter(str(exc)) from exc
    with task_service(ctx) as service:
        task = service.create_task(
            project_name=project,
            title=title,
            notes=notes,
            priority=priority,
            due_at=due_at,
            tags=tag or (),
        )
        console.print(
            f"[green]added[/green] #{task.id} {task.title} in [bold]{task.project.name}[/bold]"
        )


@app.command("list")
def list_tasks(
    ctx: typer.Context,
    project: str | None = typer.Option(None, "--project", "-p"),
    status: Status | None = typer.Option(None, "--status", "-s"),
    priority: Priority | None = typer.Option(None, "--priority"),
    tag: str | None = typer.Option(None, "--tag", "-t"),
    search: str | None = typer.Option(None, "--search", "-q", help="Match title or notes."),
    overdue: bool = typer.Option(False, "--overdue", help="Only tasks past their due date."),
    show_done: bool = typer.Option(False, "--done", help="Include completed tasks."),
) -> None:
    """List tasks, most urgent first."""
    with task_service(ctx) as service:
        tasks = service.find(
            project_name=project,
            status=status,
            priority=priority,
            tag=tag,
            search=search,
            overdue_only=overdue,
            include_done=show_done,
        )
        table = Table(title=f"{len(tasks)} task(s)")
        table.add_column("ID", style="dim", justify="right")
        table.add_column("Title")
        table.add_column("Project")
        table.add_column("Pri")
        table.add_column("Due")
        table.add_column("Tags")
        for task in tasks:
            due = task.due_at.date().isoformat() if task.due_at else ""
            if task.due_at and is_overdue(task):
                due = f"[red]{due}[/red]"
            table.add_row(
                str(task.id),
                task.title,
                task.project.name,
                task.priority.value,
                due,
                ", ".join(sorted(t.name for t in task.tags)),
            )
    console.print(table)


@app.command()
def show(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Show one task with its notes, tags and dates."""
    with task_service(ctx) as service:
        task = service.get_task(task_id)
        due = task.due_at.date().isoformat() if task.due_at else "-"
        tags = ", ".join(sorted(t.name for t in task.tags)) or "-"
        created = task.created_at.isoformat(sep=" ", timespec="minutes")
        lines = [
            f"[bold]#{task.id}[/bold] {task.title}",
            f"project:  {task.project.name}",
            f"status:   {task.status.value}",
            f"priority: {task.priority.value}",
            f"due:      {due}",
            f"tags:     {tags}",
            f"created:  {created}",
            f"notes:    {task.notes or '-'}",
        ]
    console.print("\n".join(lines))


@app.command()
def done(
    ctx: typer.Context, task_id: int = typer.Argument(..., help="Task id from `list`.")
) -> None:
    """Mark a task complete."""
    with task_service(ctx) as service:
        task = service.complete_task(task_id)
    console.print(f"[green]done[/green] #{task.id} {task.title}")


@app.command()
def reopen(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Undo a completion."""
    with task_service(ctx) as service:
        task = service.reopen_task(task_id)
    console.print(f"[cyan]reopened[/cyan] #{task.id} {task.title}")


@app.command()
def rm(ctx: typer.Context, task_id: int = typer.Argument(...)) -> None:
    """Delete a task."""
    with task_service(ctx) as service:
        task = service.delete_task(task_id)
    console.print(f"[yellow]removed[/yellow] #{task.id} {task.title}")


@app.command()
def tag(
    ctx: typer.Context,
    task_id: int = typer.Argument(...),
    names: list[str] = typer.Argument(..., help="One or more tag names."),
) -> None:
    """Add tags to a task."""
    with task_service(ctx) as service:
        task = service.tag_task(task_id, *names)
    console.print(f"[green]tagged[/green] #{task.id}: {', '.join(t.name for t in task.tags)}")


@app.command()
def untag(
    ctx: typer.Context,
    task_id: int = typer.Argument(...),
    names: list[str] = typer.Argument(..., help="One or more tag names."),
) -> None:
    """Remove tags from a task."""
    with task_service(ctx) as service:
        task = service.untag_task(task_id, *names)
    remaining = ", ".join(t.name for t in task.tags) or "no tags"
    console.print(f"[yellow]untagged[/yellow] #{task.id}: {remaining}")


@app.command()
def report(
    ctx: typer.Context,
    days: int = typer.Option(7, "--days", min=1, max=90),
    week: bool = typer.Option(False, "--week", help="Shorthand for --days 7."),
) -> None:
    """Summarise the last N days."""
    if week:
        days = 7
    with task_service(ctx) as service:
        result = service.weekly_report(days=days)
        table = Table(title=f"Last {days} days")
        table.add_column("Metric")
        table.add_column("Value", justify="right")
        table.add_row("Created", str(result.created))
        table.add_row("Completed", str(result.completed))
        table.add_row("Overdue now", str(len(result.overdue)))
        for priority, count in sorted(result.by_priority.items()):
            table.add_row(f"Open ({priority.value})", str(count))
    console.print(table)


@app.command()
def export(
    ctx: typer.Context, path: Path = typer.Argument(..., help="Destination .json file.")
) -> None:
    """Write the whole database to JSON."""
    with task_service(ctx) as service:
        payload = service.export_data()
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"[green]exported[/green] {len(payload['projects'])} project(s) to {path}")


@app.command("import")
def import_data(
    ctx: typer.Context,
    path: Path = typer.Argument(..., help="Source .json file."),
    merge: bool = typer.Option(True, "--merge/--replace", help="Skip tasks that already exist."),
) -> None:
    """Load tasks from a TaskForge JSON export."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    with task_service(ctx) as service:
        result = service.import_data(payload, merge=merge)
    console.print(
        f"[green]imported[/green] {result.projects} project(s), "
        f"{result.tasks} task(s), {result.skipped} skipped"
    )


@project_app.command("add")
def project_add(
    ctx: typer.Context,
    name: str = typer.Argument(...),
    description: str = typer.Option("", "--description", "-d"),
) -> None:
    """Create a project."""
    with task_service(ctx) as service:
        project = service.create_project(name, description)
    console.print(f"[green]created[/green] project [bold]{project.name}[/bold]")


@project_app.command("list")
def project_list(
    ctx: typer.Context,
    show_archived: bool = typer.Option(False, "--all", "-a", help="Include archived projects."),
) -> None:
    """List projects with task counts."""
    with task_service(ctx) as service:
        projects = service.list_projects(include_archived=show_archived)
        table = Table(title="Projects")
        table.add_column("Name")
        table.add_column("Open", justify="right")
        table.add_column("Archived")
        for project in projects:
            open_count = sum(1 for t in project.tasks if t.status is Status.TODO)
            table.add_row(project.name, str(open_count), "yes" if project.archived else "")
    console.print(table)


@project_app.command("archive")
def project_archive(ctx: typer.Context, name: str = typer.Argument(...)) -> None:
    """Archive a project; its tasks become read-only."""
    with task_service(ctx) as service:
        project = service.archive_project(name)
    console.print(f"[yellow]archived[/yellow] [bold]{project.name}[/bold]")


@project_app.command("rm")
def project_rm(
    ctx: typer.Context,
    name: str = typer.Argument(...),
    force: bool = typer.Option(False, "--force", "-f", help="Do not ask for confirmation."),
) -> None:
    """Delete a project and all of its tasks."""
    if not force:
        typer.confirm(f"Delete project {name!r} and all its tasks?", abort=True)
    with task_service(ctx) as service:
        service.delete_project(name)
    console.print(f"[yellow]deleted[/yellow] project {name}")


if __name__ == "__main__":
    app()
```

```python
# src/taskforge/__init__.py
"""TaskForge - a personal task manager for the command line."""

__version__ = "0.1.0"

__all__ = ["__version__"]
```

```python
# src/taskforge/__main__.py
from taskforge.cli import app

if __name__ == "__main__":
    app()
```

Now use it:

```bash
taskforge project add work --description "Day job"
taskforge add "Write the quarterly report" -p work --priority high --due +3d -t writing -t q3
taskforge add "Email Dana about the contract" -p work --due today
taskforge add "Buy paint" -p home --priority low
taskforge list
```

```text
                                    3 task(s)
 ID  Title                        Project  Pri     Due         Tags
  2  Email Dana about the contract work     medium  2026-09-07
  1  Write the quarterly report    work     high    2026-09-10   q3, writing
  3  Buy paint                     home     low
```

```bash
taskforge done 2
taskforge show 1
taskforge untag 1 q3
taskforge list --overdue
taskforge report --week
taskforge export ~/taskforge-backup.json
```

```bash
taskforge --help
taskforge add --help
```

The `--help` text is generated from the docstrings and `help=` strings you already wrote. That is
the argument for putting them there instead of in a README nobody reads.

:::tip Exit codes are part of the interface
`taskforge done 999` prints `error: no task with id #999` to stderr and exits `1`. Anything that
wraps your CLI — a shell script, a cron job, CI — checks that. Bad *arguments* are a different
failure from a failed command: `taskforge add "x" --due "next tuesday"` raises
`typer.BadParameter`, which prints the usage block plus the message and exits `2` — the
conventional code for "you typed it wrong", against `1` for "I tried and it failed". Print
user-facing errors to stderr (`err_console`), results to stdout, and never `sys.exit(0)` on
failure.
:::

## Milestone 7 — Migrations

`create_all()` creates tables that do not exist and does nothing else. It cannot add a column to
a table that already has rows. The day you ship a schema change you need migrations.

Alembic is the real answer. For one SQLite file, here is the same idea in forty lines, which also
teaches you what Alembic is doing:

```python
# src/taskforge/migrations.py
"""Ordered, one-way schema migrations.

Each entry takes the schema from version N-1 to N. Never edit a released
migration; add a new one.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import Connection, Engine, text


def _v1_initial(conn: Connection) -> None:
    from taskforge.models import Base

    Base.metadata.create_all(conn)


MIGRATIONS: list[Callable[[Connection], None]] = [_v1_initial]


def ensure_schema(engine: Engine) -> None:
    """Bring the database up to the newest migration, then stop."""
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"))
        current = conn.execute(text("SELECT version FROM schema_version")).scalar()
        if current is None:
            conn.execute(text("INSERT INTO schema_version (version) VALUES (0)"))
            current = 0
        for version, step in enumerate(MIGRATIONS, start=1):
            if version > current:
                step(conn)
                conn.execute(text("UPDATE schema_version SET version = :v"), {"v": version})
```

:::warning Pass the migration's connection to `create_all`, not its engine
`conn.engine` looks like the natural argument to `create_all()` — it is the same engine, after
all. It is also the one mistake that makes TaskForge die on its very first command against a
fresh database:

```text
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
```

`ensure_schema` is holding an open write transaction on `conn` (it just created and inserted into
`schema_version`). `conn.engine` then opens a **second** SQLite connection to write the tables,
and that connection cannot get the write lock while the first transaction is still open. SQLite
allows many readers and exactly one writer; two connections from the same process get no special
treatment. Pass `conn` and the DDL joins the transaction you are already in.
:::

Later, when you add a `recurring` column, you append one function:

```python
def _v2_add_recurring(conn: Connection) -> None:
    conn.execute(text("ALTER TABLE tasks ADD COLUMN recurring TEXT"))


MIGRATIONS = [_v1_initial, _v2_add_recurring]
```

Each entry is identified by its **position** in `MIGRATIONS`, not by its name, so a version
number is only a label you use to keep the file readable. If your schema never got the
`recurring` column, ship the list without `_v2_add_recurring` instead of renumbering anything.

For a project with more than one user, use Alembic instead:

```bash
python3 -m pip install alembic
alembic init migrations
alembic revision --autogenerate -m "add recurring column"
alembic upgrade head
```

## Milestone 8 — Tests

```python
# tests/conftest.py
from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from taskforge.db import make_session_factory
from taskforge.models import Base
from taskforge.repository import TaskRepository
from taskforge.services import TaskService


@pytest.fixture()
def session_factory(tmp_path) -> Iterator[sessionmaker[Session]]:
    """A brand-new SQLite database per test, in pytest's temp directory."""
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", future=True)
    Base.metadata.create_all(engine)
    yield make_session_factory(engine)
    engine.dispose()


@pytest.fixture()
def session(session_factory) -> Iterator[Session]:
    db_session = session_factory()
    yield db_session
    db_session.close()


@pytest.fixture()
def repo(session) -> TaskRepository:
    return TaskRepository(session)


@pytest.fixture()
def service(repo) -> TaskService:
    return TaskService(repo)
```

One database per test, created fresh, deleted with `tmp_path`. No fixtures file to maintain, no
ordering surprises, no "why does this pass alone and fail in the suite".

```python
# tests/test_repository.py
from datetime import datetime

from taskforge.models import Priority
from taskforge.repository import TaskRepository


def test_project_names_are_unique_per_lookup(repo: TaskRepository) -> None:
    repo.add_project("work")
    assert repo.get_project("work") is not None
    assert repo.get_project("nope") is None


def test_list_tasks_filters_by_tag(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    home = repo.add_project("home")
    report = repo.add_task(work, "Write report", priority=Priority.HIGH)
    repo.add_task(home, "Buy milk")
    report.tags.append(repo.get_or_create_tag("writing"))

    found = repo.list_tasks(project=work, tag="writing")

    assert [t.title for t in found] == ["Write report"]


def test_list_tasks_orders_by_due_date_with_missing_last(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    later = repo.add_task(work, "Later", due_at=datetime(2026, 12, 1))
    sooner = repo.add_task(work, "Sooner", due_at=datetime(2026, 1, 1))
    never = repo.add_task(work, "No date")

    assert [t.id for t in repo.list_tasks(project=work)] == [sooner.id, later.id, never.id]


def test_search_matches_title_and_notes_case_insensitively(repo: TaskRepository) -> None:
    work = repo.add_project("work")
    repo.add_task(work, "Renew passport", notes="bring the old one")

    assert len(repo.list_tasks(project=work, search="PASSPORT")) == 1
    assert len(repo.list_tasks(project=work, search="old one")) == 1
    assert len(repo.list_tasks(project=work, search="visa")) == 0
```

```python
# tests/test_services.py
from datetime import datetime

import pytest

from taskforge.models import Priority, Status
from taskforge.services import (
    ProjectArchivedError,
    TaskService,
    ValidationError,
    is_overdue,
)


def test_create_task_makes_the_project_on_demand(service: TaskService) -> None:
    task = service.create_task("home", "Buy paint", priority=Priority.LOW)

    assert task.project.name == "home"
    assert task.priority is Priority.LOW
    assert task.status is Status.TODO


def test_blank_title_is_rejected(service: TaskService) -> None:
    with pytest.raises(ValidationError):
        service.create_task("home", "   ")


def test_completing_a_task_stamps_completed_at(service: TaskService) -> None:
    task = service.create_task("work", "Ship it")

    done = service.complete_task(task.id)

    assert done.status is Status.DONE
    assert done.completed_at is not None


def test_cannot_complete_a_task_in_an_archived_project(service: TaskService) -> None:
    task = service.create_task("work", "Old thing")
    service.archive_project("work")

    with pytest.raises(ProjectArchivedError):
        service.complete_task(task.id)


def test_overdue_uses_date_not_time(service: TaskService) -> None:
    today = service.create_task("work", "Today", due_at=datetime(2026, 9, 7))
    last_week = service.create_task("work", "Late", due_at=datetime(2026, 9, 1))
    now = datetime(2026, 9, 7, 23, 59)

    assert not is_overdue(today, now)  # due today is not overdue at 23:59
    assert is_overdue(last_week, now)


def test_find_sorts_urgent_first(service: TaskService) -> None:
    service.create_task("work", "Meh", priority=Priority.LOW)
    service.create_task("work", "Now", priority=Priority.URGENT)
    service.create_task("work", "Soon", priority=Priority.HIGH)

    titles = [t.title for t in service.find()]

    assert titles == ["Now", "Soon", "Meh"]


def test_weekly_report_counts_created_and_completed(service: TaskService) -> None:
    task = service.create_task("work", "Older")
    service.complete_task(task.id)
    service.create_task("work", "Fresh")

    result = service.weekly_report(days=7, now=datetime(2026, 9, 7, 12, 0))

    assert result.created == 2
    assert result.completed == 1


def test_export_then_import_round_trips(service: TaskService) -> None:
    service.create_task("work", "Write docs", tags=["writing"])

    payload = service.export_data()
    result = service.import_data(payload, merge=False)

    assert result.tasks == 1
    assert [t.title for t in service.find(include_done=True)] == [
        "Write docs",
        "Write docs",
    ]
```

```python
# tests/test_cli.py
from __future__ import annotations

from typer.testing import CliRunner

from taskforge.cli import app

runner = CliRunner()


def test_add_then_list_shows_the_task(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TASKFORGE_DB", f"sqlite:///{tmp_path / 'cli.db'}")
    monkeypatch.setenv("TASKFORGE_LOG", str(tmp_path / "cli.log"))

    added = runner.invoke(
        app, ["add", "Write the report", "--project", "work", "--priority", "high"]
    )
    assert added.exit_code == 0, added.output
    assert "Write the report" in added.output

    listed = runner.invoke(app, ["list", "--project", "work"])
    assert listed.exit_code == 0, listed.output
    assert "Write the report" in listed.output


def test_unknown_task_exits_non_zero(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TASKFORGE_DB", f"sqlite:///{tmp_path / 'cli.db'}")
    monkeypatch.setenv("TASKFORGE_LOG", str(tmp_path / "cli.log"))

    result = runner.invoke(app, ["done", "999"])

    assert result.exit_code == 1
    assert "no task with id #999" in result.output
```

```bash
python3 -m pytest
```

```text
15 passed in 0.50s
```

The CLI test works because `CliRunner` invokes the app in-process and `Settings.from_env()` picks
up the environment variables we patched — the same mechanism that lets a user point TaskForge at
a different database without editing any code.

:::scenario "Users want to re-open a task they completed by mistake."
It ships as a bug report two days after release: `done 12` was a misclick and now the task is
gone from `list`. The data is still there — only the status changed.
:::

:::solution Add `reopen`, and make the rule explicit
The service already has `reopen_task`, so this is a UI gap plus one policy question: should a
reopened task keep its original `completed_at`? No — `completed_at` records the *current*
completion. Clear it.

The command is one call to that method, so it belongs with the other commands in Milestone 6:
`taskforge reopen 12`. A command that the brief promises but nobody wired up is not a bug fix, it
is a missing feature, so it never belonged in this box. What the bug report genuinely adds is the
test that pins the policy down:

```python
def test_reopen_clears_completed_at(service: TaskService) -> None:
    task = service.create_task("work", "Ship it")
    service.complete_task(task.id)

    reopened = service.reopen_task(task.id)

    assert reopened.status is Status.TODO
    assert reopened.completed_at is None
```

Note how little moved: one command, one test, zero repository changes in this box. That is the layering doing
its job. The harder version of this request — "undo the last thing I did, whatever it was" — is
the same shape but needs an audit log: add an `events` table recording
`(task_id, action, at, payload)` and replay backwards. Decide now whether you want that, because
retrofitting an audit log after six months of deletions is impossible.
:::

:::scenario "Tags are exploding: `work`, `Work`, `WORK`, and `work-urgent` are all in the list."
Tag autocomplete is now useless and `list --tag work` silently returns a subset. You need to
merge existing duplicates without breaking tasks that reference them.
:::

:::solution Normalise on write, then migrate the data
Two changes: stop the bleeding, then clean up.

First, normalise at the boundary. In `create_task` and `tag_task` the code already calls
`.strip().lower()` — keep that, and move it into the repository so no caller can forget:

```python
def get_or_create_tag(self, name: str) -> Tag:
    normalised = name.strip().lower()
    tag = self.session.scalar(select(Tag).where(Tag.name == normalised))
    if tag is None:
        tag = Tag(name=normalised)
        self.session.add(tag)
        self.session.flush()
    return tag
```

Now remove the `.lower()` calls from `services.py` — one place owns the rule.

Second, merge the existing rows. This is a data migration, so it goes in `migrations.py`:

```python
def _v3_merge_duplicate_tags(conn: Connection) -> None:
    """Collapse tags that differ only by case, keeping the oldest id."""
    rows = conn.execute(text("SELECT id, name FROM tags ORDER BY id")).fetchall()
    canonical: dict[str, int] = {}
    for tag_id, name in rows:
        key = name.strip().lower()
        canonical_id = canonical.setdefault(key, tag_id)
        if canonical_id == tag_id:
            continue
        conn.execute(
            text("UPDATE OR IGNORE task_tag SET tag_id = :keep WHERE tag_id = :drop"),
            {"keep": canonical_id, "drop": tag_id},
        )
        conn.execute(text("DELETE FROM task_tag WHERE tag_id = :drop"), {"drop": tag_id})
        conn.execute(text("DELETE FROM tags WHERE id = :drop"), {"drop": tag_id})

    # The duplicates are gone, so the survivor can take the normalised spelling.
    for key, keep in canonical.items():
        conn.execute(
            text("UPDATE tags SET name = :norm WHERE id = :keep"),
            {"norm": key, "keep": keep},
        )


MIGRATIONS = [_v1_initial, _v2_add_recurring, _v3_merge_duplicate_tags]
```

It is called `_v3` because `_v2_add_recurring` already claimed that slot earlier in the chapter.
Add whichever version your own schema needs and leave the other out: the version number is the
entry's position in `MIGRATIONS`, not the digit in its name.

Two details make this work. Renaming the survivor is not optional: leave `Work` in place and the
next `get_or_create_tag("work")` inserts a brand-new row, because every write from now on is
lower-cased — you would be back to two tags tomorrow. And the renames have to happen *after* the
deletes, since `tags.name` is `UNIQUE` and `UPDATE tags SET name = 'work'` on the survivor
collides with the duplicate that is still sitting there.

`UPDATE OR IGNORE` is SQLite's way of skipping rows that would violate the composite primary key
on `task_tag` — a task already carrying the surviving tag simply keeps it. On Postgres you would
write `ON CONFLICT DO NOTHING`.

Back up before running it, and test the migration against a copy of a real export:

```bash
taskforge export ~/taskforge-backup.json
```

The lesson generalises: normalisation belongs at the write boundary, de-duplication belongs in a
migration, and both are far cheaper than cleaning up four spellings in six months.
:::

:::pitfall Two sessions, one object
The bug that will cost you an hour: you create a `Session` somewhere, load a task, and then
another part of the code (a test helper, a second command) opens its own session and modifies the
same row. Your object still shows the old value, or you get
`DetachedInstanceError: Parent instance <Task> is not bound to a Session`.

Rules that avoid it:

1. One session per unit of work — one per CLI invocation, one per test. `session_scope` enforces
   this; do not call `sessionmaker()` in two places.
2. Do not pass model objects across the session boundary. Pass **ids** (`task_id: int`), not
   `Task` instances.
3. Finish reading objects before the `with` block ends (build the rich `Table` inside it, as
   `list` does), or keep `expire_on_commit=False` so attributes stay loaded.
4. In tests, never share a `Task` between two fixtures that use different sessions. Re-fetch by
   id.
:::

## Key takeaways

- A layered application (CLI → services → repository → models) keeps rules testable and storage
  swappable; nothing lower-level imports anything higher.
- All SQL lives in the repository. All rules live in the service. All formatting lives in the CLI.
  When you are unsure where a line belongs, that sentence decides it.
- `session_scope` centralises commit, rollback, and close, so no caller can leave a partial
  transaction behind.
- Store UTC as naive datetimes in SQLite, compare due dates by `date()`, and let a helper like
  `parse_due` own the human-facing formats — resolved on the same UTC clock the comparison uses,
  or `--due today` is overdue before lunch.
- Enums for status and priority make illegal states unrepresentable and typos impossible.
- Typer generates `--help` from your docstrings and `help=` strings, so documentation is a
  by-product of writing the command.
- Exit codes are part of the CLI contract: `0` for success, non-zero with a stderr message for
  every failure.
- Tests get a fresh SQLite file in `tmp_path`, which makes them fast, isolated, and order
  independent.

## Milestone checklist

- [ ] `pyproject.toml` with metadata, dependencies, `[project.scripts]`, and `[tool.*]` config
      for ruff, mypy, and pytest.
- [ ] `src/taskforge/models.py`: `Project`, `Tag`, `Task`, the `task_tag` association table,
      `Status`/`Priority` enums, `PRIORITY_RANK`, and `utcnow()`.
- [ ] `config.py` reading `TASKFORGE_DB` and `TASKFORGE_LOG`, creating parent directories.
- [ ] `db.py` with `create_engine_from_settings` (SQLite foreign keys on), `make_session_factory`,
      and `session_scope`.
- [ ] `logging_setup.py` configuring only the `taskforge` logger.
- [ ] `repository.py` with `TaskRepository`: projects, tasks with all six filters, tags, and the
      three report queries.
- [ ] `services.py` with `TaskService`, the four error types, `is_overdue`, `find`,
      `weekly_report`, `export_data`, `import_data`, `tag_task`/`untag_task`, and `get_task`.
- [ ] `dates.py` with `parse_due` supporting `today`, `tomorrow`, `+3d`, and `YYYY-MM-DD`,
      resolved against the UTC date.
- [ ] `cli.py` with `add`, `list`, `show`, `done`, `reopen`, `rm`, `tag`, `untag`, `report`,
      `export`, `import`, and the `project` sub-app; `--version`, `--verbose`, and a `--week`
      shortcut on `report`.
- [ ] `migrations.py` with `ensure_schema` and a versioned `MIGRATIONS` list, each step using the
      connection it is given.
- [ ] Tests: repository filters and ordering, service rules (archived project, overdue, sort
      order, export/import round trip), and at least one CLI test through `CliRunner`.
- [ ] `ruff check . && ruff format --check . && mypy src` all clean (with the bugbear setting
      above), and `pytest` reporting `15 passed`.
- [ ] `python3 -m build` succeeds and the built wheel installs into a fresh venv where
      `taskforge --help` works.
- [ ] A tag and a first release: `git tag -a v0.1.0 -m "TaskForge 0.1.0"`.

## Where to take it next

- **Web UI** — Chapter 30 (StudyHub) puts a FastAPI and HTMX front end on exactly this shape of
  service layer. If you keep `TaskService` free of CLI concerns, you reuse it unchanged.
- **Sync** — export to JSON, put the file in Dropbox or a gist, import on the other machine. The
  hard part is conflict resolution on simultaneous edits; start by last-write-wins on
  `updated_at` and only get clever if that actually hurts.
- **Reminders** — a `notify` command plus `cron` (macOS/Linux) or Task Scheduler (Windows) that
  runs `taskforge list --overdue` and pipes it to your notifier. No daemon needed.
- **Richer queries** — saved views ("today", "this week", "waiting on Dana") defined as named
  filter sets in config, so `taskforge list --view today` works.
- **Postgres** — change `TASKFORGE_DB` to a `postgresql+psycopg://` URL. If nothing breaks, your
  layering is correct. If something breaks, it will be a raw string comparison or a SQLite-only
  function, and you will find it in the repository — which is the only file you need to read.
- **Full-text search** — SQLite FTS5 or Postgres `tsvector` behind a new repository method, with
  the plain `ilike` version kept as a fallback.

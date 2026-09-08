"""Business rules. Talks to a TaskRepository, knows nothing about SQL or Typer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, time

from taskforge.models import PRIORITY_RANK, Priority, Project, Status, Tag, Task, utcnow
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
        task = self.repo.add_task(
            project, title, notes=notes, priority=priority, due_at=due_at
        )
        for name in tags:
            task.tags.append(self.repo.get_or_create_tag(name.strip().lower()))
        return task

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

    def export_data(self) -> dict:
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

    def import_data(self, payload: dict, *, merge: bool = True) -> ImportResult:
        if payload.get("version") != 1:
            raise ValidationError(f"unsupported export version: {payload.get('version')!r}")

        projects = tasks = skipped = 0
        for raw_project in payload.get("projects", []):
            name = self._clean_name(raw_project.get("name", ""), "project name")
            project = self.repo.get_project(name)
            if project is None:
                project = self.repo.add_project(name, raw_project.get("description", ""))
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

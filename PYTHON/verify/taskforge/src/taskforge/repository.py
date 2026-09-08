"""All SQL in TaskForge. Nothing here makes policy decisions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskforge.models import Priority, Project, Status, Tag, Task


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
    ) -> Task:
        task = Task(
            project=project, title=title, notes=notes, priority=priority, due_at=due_at
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
            stmt = stmt.join(Task.tags).where(Tag.name == tag)
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

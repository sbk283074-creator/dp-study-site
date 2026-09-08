"""Database models for TaskForge.

All timestamps are stored as *naive* UTC datetimes. SQLite has no time zone
type, so an "aware" column buys nothing and costs you "can't compare
offset-naive and offset-aware" errors. Store UTC; convert at the edges only.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (SQLite-safe)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Declarative base shared by every TaskForge model."""


class Status(str, enum.Enum):
    TODO = "todo"
    DONE = "done"


class Priority(str, enum.Enum):
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

    tasks: Mapped[list[Task]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

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
